from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from ..db import get_db
from ..dependencies import require_assistente_or_admin
from ..models.org import Org
from ..models.user import Role, User
from ..schemas.user import (
    BeneficiarioCreate,
    BeneficiarioUpdate,
    UserListResponse,
    UserResponse,
    VincularBeneficiarioRequest,
)
from ..security import hash_password

router = APIRouter(prefix="/beneficiarios", tags=["beneficiarios"])


def _ensure_assistente(db: Session, assistente_id: int) -> User:
    assistente = (
        db.query(User)
        .filter(User.id == assistente_id, User.role == Role.ASSISTENTE, User.is_active == True)
        .first()
    )
    if not assistente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assistente não encontrado ou inativo",
        )
    return assistente


def _ensure_org(db: Session, org_id: int) -> Org:
    org = db.query(Org).filter(Org.id == org_id).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ONG não encontrada")
    return org


@router.get("", response_model=UserListResponse)
def list_beneficiarios(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    assistente_id: int | None = None,
    current_user: User = Depends(require_assistente_or_admin),
    db: Session = Depends(get_db),
) -> UserListResponse:
    query = db.query(User).filter(User.role == Role.BENEFICIARIO)

    if current_user.role == Role.ASSISTENTE:
        query = query.filter(User.assistente_id == current_user.id)
    elif assistente_id is not None:
        query = query.filter(User.assistente_id == assistente_id)

    if search:
        like = f"%{search.lower()}%"
        query = query.filter(
            or_(
                func.lower(User.name).like(like),
                func.lower(User.social_name).like(like),
                func.lower(User.email).like(like),
                User.cpf.like(f"%{search}%"),
            )
        )

    total = query.count()
    beneficiarios = (
        query.order_by(User.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return UserListResponse(users=beneficiarios, total=total, page=page, page_size=page_size)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_beneficiario(
    data: BeneficiarioCreate,
    current_user: User = Depends(require_assistente_or_admin),
    db: Session = Depends(get_db),
) -> UserResponse:
    existing_email = db.query(User).filter(User.email == data.email).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já cadastrado")

    if data.cpf:
        existing_cpf = db.query(User).filter(User.cpf == data.cpf).first()
        if existing_cpf:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CPF já cadastrado")

    assistente_id = data.assistente_id
    if current_user.role == Role.ASSISTENTE:
        if data.assistente_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Assistente só pode criar beneficiário vinculado a si mesmo",
            )
        assistente_id = current_user.id
    else:
        _ensure_assistente(db, assistente_id)

    if data.org_id is not None:
        _ensure_org(db, data.org_id)

    beneficiario = User(
        email=data.email,
        name=data.name,
        social_name=data.social_name,
        cpf=data.cpf,
        password_hash=hash_password(data.password),
        role=Role.BENEFICIARIO,
        assistente_id=assistente_id,
        org_id=data.org_id,
        is_active=True,
    )
    db.add(beneficiario)
    db.commit()
    db.refresh(beneficiario)
    return beneficiario


@router.put("/{beneficiario_id}", response_model=UserResponse)
def update_beneficiario(
    beneficiario_id: int,
    data: BeneficiarioUpdate,
    current_user: User = Depends(require_assistente_or_admin),
    db: Session = Depends(get_db),
) -> UserResponse:
    beneficiario = (
        db.query(User)
        .filter(User.id == beneficiario_id, User.role == Role.BENEFICIARIO)
        .first()
    )
    if not beneficiario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Beneficiário não encontrado")

    if current_user.role == Role.ASSISTENTE and beneficiario.assistente_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Assistente só pode gerenciar seus beneficiários",
        )

    update_data = data.model_dump(exclude_unset=True)

    if "email" in update_data and update_data["email"] != beneficiario.email:
        existing = db.query(User).filter(User.email == update_data["email"]).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado",
            )

    if "cpf" in update_data and update_data["cpf"] != beneficiario.cpf:
        existing = db.query(User).filter(User.cpf == update_data["cpf"]).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF já cadastrado",
            )

    if "assistente_id" in update_data:
        new_assistente_id = update_data["assistente_id"]
        if current_user.role == Role.ASSISTENTE and new_assistente_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Assistente não pode vincular beneficiário a outro assistente",
            )
        if new_assistente_id is not None:
            _ensure_assistente(db, new_assistente_id)
        elif current_user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas administradores podem desvincular beneficiários",
            )

    if "org_id" in update_data and update_data["org_id"] is not None:
        _ensure_org(db, update_data["org_id"])

    for field, value in update_data.items():
        setattr(beneficiario, field, value)

    db.commit()
    db.refresh(beneficiario)
    return beneficiario


@router.post("/vincular", response_model=UserResponse)
def vincular_beneficiario(
    payload: VincularBeneficiarioRequest,
    current_user: User = Depends(require_assistente_or_admin),
    db: Session = Depends(get_db),
) -> UserResponse:
    beneficiario = (
        db.query(User)
        .filter(User.id == payload.beneficiario_id, User.role == Role.BENEFICIARIO)
        .first()
    )
    if not beneficiario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Beneficiário não encontrado")

    if current_user.role == Role.ASSISTENTE:
        if payload.assistente_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Assistente não pode vincular beneficiário a outro assistente",
            )
        if beneficiario.assistente_id not in (None, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Beneficiário já vinculado a outro assistente",
            )

    _ensure_assistente(db, payload.assistente_id)
    beneficiario.assistente_id = payload.assistente_id
    db.commit()
    db.refresh(beneficiario)
    return beneficiario
