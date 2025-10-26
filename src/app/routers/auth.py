from fastapi import APIRouter, Depends, HTTPException, status
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

router = APIRouter(prefix="/auth", tags=["auth"])


# =============== Register ===============

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Registra novo usuário (beneficiário por padrão)"""
    # Verificar se email já existe
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )

    # Verificar CPF se fornecido
    if data.cpf:
        existing_cpf = db.query(User).filter(User.cpf == data.cpf).first()
        if existing_cpf:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF já cadastrado"
            )

    # Criar usuário
    user = User(
        email=data.email,
        name=data.name,
        social_name=data.social_name,
        cpf=data.cpf,
        password_hash=hash_password(data.password),
        role=Role.BENEFICIARIO,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

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
