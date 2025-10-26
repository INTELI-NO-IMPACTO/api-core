from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..db import get_db
from ..models.user import User, Role
from ..models.token import RefreshToken
from ..models.chat import Chat
from ..security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_session_id
)
from ..schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    RefreshTokenRequest,
    AccessTokenResponse,
    AnonymousSessionRequest,
    AnonymousSessionResponse,
    CurrentUserResponse,
)
from ..dependencies import get_current_user
from ..config import settings
from ..utils.supabase import get_supabase_storage_service

router = APIRouter(prefix="/auth", tags=["auth"])


# =============== Register ===============

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    social_name: str | None = Form(None),
    pronoun: str | None = Form(None),
    cpf: str | None = Form(None),
    profile_image: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):
    """
    Registra novo usuário (beneficiário por padrão).

    Aceita dados do usuário via form-data, incluindo upload opcional de foto de perfil.
    """
    # Validar senha
    if len(password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha deve ter no mínimo 6 caracteres"
        )

    # Validar e normalizar CPF se fornecido
    normalized_cpf = None
    if cpf:
        normalized_cpf = ''.join(filter(str.isdigit, cpf))
        if len(normalized_cpf) != 11:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF deve ter 11 dígitos"
            )

    # Verificar se email já existe
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )

    # Verificar CPF se fornecido
    if normalized_cpf:
        existing_cpf = db.query(User).filter(User.cpf == normalized_cpf).first()
        if existing_cpf:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF já cadastrado"
            )

    # Criar usuário
    user = User(
        email=email,
        name=name,
        social_name=social_name,
        pronoun=pronoun,
        cpf=normalized_cpf,
        password_hash=hash_password(password),
        role=Role.BENEFICIARIO,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Upload de imagem de perfil se fornecida
    if profile_image:
        # Validar que é uma imagem
        if profile_image.content_type and profile_image.content_type.startswith("image/"):
            try:
                storage_service = get_supabase_storage_service()

                # Ler arquivo e fazer upload
                file_bytes = await profile_image.read()

                # Sanitizar nome do arquivo
                from pathlib import Path
                path = Path(profile_image.filename or "profile.jpg")
                ext = path.suffix or ".jpg"
                safe_filename = f"profile_{user.id}{ext}"

                destination = f"users/{user.id}/profile/{safe_filename}"

                stored_path = storage_service.upload_file(
                    destination,
                    file_bytes,
                    content_type=profile_image.content_type,
                    upsert=True,
                )

                # Gerar URL pública
                public_url = storage_service.get_public_url(stored_path)

                # Atualizar usuário com URL da imagem
                user.profile_image_url = public_url
                db.commit()
                db.refresh(user)
            except HTTPException:
                # Se falhar o upload, continua sem a imagem
                pass

    # Criar tokens
    access_token = create_access_token(user.id)
    refresh_token_str = create_refresh_token(user.id)

    # Salvar refresh token no banco
    refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token_str,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(refresh_token)
    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRES_MIN * 60
    )


# =============== Login ===============

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Login com email e senha"""
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )

    # Criar tokens
    access_token = create_access_token(user.id)
    refresh_token_str = create_refresh_token(user.id)

    # Salvar refresh token no banco
    refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token_str,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(refresh_token)
    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRES_MIN * 60
    )


# =============== Refresh Token ===============

@router.post("/refresh", response_model=AccessTokenResponse)
def refresh_access_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Renova access token usando refresh token"""
    # Decodificar e validar refresh token
    payload = decode_token(data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido"
        )

    # Verificar se refresh token existe e não foi revogado
    refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token == data.refresh_token,
        RefreshToken.is_revoked == False
    ).first()

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou revogado"
        )

    # Verificar se expirou
    if refresh_token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expirado"
        )

    # Criar novo access token
    user_id = int(payload.get("sub"))
    access_token = create_access_token(user_id)

    return AccessTokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRES_MIN * 60
    )


# =============== Current User ===============

@router.get("/me", response_model=CurrentUserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Retorna dados do usuário logado"""
    return CurrentUserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        social_name=current_user.social_name,
        pronoun=current_user.pronoun,
        profile_image_url=current_user.profile_image_url,
        role=current_user.role.value,
        is_active=current_user.is_active,
        org_id=current_user.org_id,
        assistente_id=current_user.assistente_id
    )


@router.put("/me", response_model=CurrentUserResponse)
async def update_me(
    name: str | None = Form(None),
    social_name: str | None = Form(None),
    pronoun: str | None = Form(None),
    cpf: str | None = Form(None),
    profile_image: UploadFile | None = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza dados do usuário logado.

    Permite atualizar: name, social_name, pronoun, cpf e profile_image.
    Todos os campos são opcionais - apenas os fornecidos serão atualizados.
    """
    # Atualizar campos de texto se fornecidos
    if name is not None:
        current_user.name = name

    if social_name is not None:
        current_user.social_name = social_name

    if pronoun is not None:
        current_user.pronoun = pronoun

    if cpf is not None:
        # Validar e normalizar CPF
        normalized_cpf = ''.join(filter(str.isdigit, cpf))
        if len(normalized_cpf) != 11:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF deve ter 11 dígitos"
            )

        # Verificar se CPF já está em uso por outro usuário
        existing_cpf = db.query(User).filter(
            User.cpf == normalized_cpf,
            User.id != current_user.id
        ).first()

        if existing_cpf:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF já cadastrado para outro usuário"
            )

        current_user.cpf = normalized_cpf

    # Upload de imagem de perfil se fornecida
    if profile_image:
        # Validar que é uma imagem
        if not profile_image.content_type or not profile_image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O arquivo deve ser uma imagem (image/*)"
            )

        try:
            storage_service = get_supabase_storage_service()

            # Ler arquivo e fazer upload
            file_bytes = await profile_image.read()

            # Sanitizar nome do arquivo
            from pathlib import Path
            path = Path(profile_image.filename or "profile.jpg")
            ext = path.suffix or ".jpg"
            safe_filename = f"profile_{current_user.id}{ext}"

            destination = f"users/{current_user.id}/profile/{safe_filename}"

            stored_path = storage_service.upload_file(
                destination,
                file_bytes,
                content_type=profile_image.content_type,
                upsert=True,
            )

            # Gerar URL pública
            public_url = storage_service.get_public_url(stored_path)
            current_user.profile_image_url = public_url
        except HTTPException as exc:
            if exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Storage não configurado para upload de arquivos."
                ) from exc
            raise

    # Salvar alterações
    db.commit()
    db.refresh(current_user)

    return CurrentUserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        social_name=current_user.social_name,
        pronoun=current_user.pronoun,
        profile_image_url=current_user.profile_image_url,
        role=current_user.role.value,
        is_active=current_user.is_active,
        org_id=current_user.org_id,
        assistente_id=current_user.assistente_id
    )


# =============== Anonymous Session ===============

@router.post("/anonymous-session", response_model=AnonymousSessionResponse, status_code=status.HTTP_201_CREATED)
def create_anonymous_session(data: AnonymousSessionRequest, db: Session = Depends(get_db)):
    """Cria sessão anônima para chat sem login"""
    # Gerar ID de sessão único
    session_id = generate_session_id()

    # Criar chat anônimo
    chat = Chat(
        user_id=None,
        session_id=session_id,
        is_active=True
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)

    return AnonymousSessionResponse(
        session_id=session_id,
        chat_id=chat.id,
        expires_in=3600 * 24  # 24 horas
    )


# =============== Logout ===============

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    data: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoga refresh token (logout)"""
    refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token == data.refresh_token,
        RefreshToken.user_id == current_user.id
    ).first()

    if refresh_token:
        refresh_token.is_revoked = True
        refresh_token.revoked_at = datetime.utcnow()
        db.commit()

    return None


# =============== Profile Image Upload ===============

@router.post("/upload-profile-image", response_model=CurrentUserResponse)
async def upload_profile_image(
    profile_image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload de foto de perfil do usuário.

    Aceita apenas imagens (image/*) e salva no Supabase Storage.
    """
    # Validar que é uma imagem
    if not profile_image.content_type or not profile_image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O arquivo deve ser uma imagem (image/*)"
        )

    # Obter serviço de storage
    try:
        storage_service = get_supabase_storage_service()
    except HTTPException as exc:
        if exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Storage não configurado para upload de arquivos."
            ) from exc
        raise

    # Ler arquivo e fazer upload
    file_bytes = await profile_image.read()

    # Sanitizar nome do arquivo
    import re
    from pathlib import Path

    path = Path(profile_image.filename or "profile.jpg")
    ext = path.suffix or ".jpg"
    # Usar ID do usuário para garantir unicidade
    safe_filename = f"profile_{current_user.id}{ext}"

    destination = f"users/{current_user.id}/profile/{safe_filename}"

    stored_path = storage_service.upload_file(
        destination,
        file_bytes,
        content_type=profile_image.content_type,
        upsert=True,  # Permite sobrescrever imagem anterior
    )

    # Gerar URL pública
    public_url = storage_service.get_public_url(stored_path)

    # Atualizar usuário no banco
    current_user.profile_image_url = public_url
    db.commit()
    db.refresh(current_user)

    return current_user
