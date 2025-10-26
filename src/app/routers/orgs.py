from fastapi import APIRouter, Depends, HTTPException, Query, status
from datetime import datetime

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..dependencies import get_current_user
from ..models.org import Org
from ..models.user import User
from ..schemas.org import (
    ApproveOrgRequest,
    InviteOrgByEmailRequest,
    InviteOrgByEmailResponse,
    OrgApprovalResponse,
    OrgCreate,
    OrgListResponse,
    OrgResponse,
    OrgUpdate,
    ResendInviteRequest,
    ValidateInviteCodeRequest,
    ValidateInviteCodeResponse,
)
from ..security import generate_invite_code
from ..utils.email import (
    EmailNotConfiguredError,
    EmailService,
    get_email_service,
    send_invite_email,
    send_org_validation_email,
)

router = APIRouter(prefix="/orgs", tags=["orgs"])


def _generate_unique_invite_code(db: Session) -> str:
    while True:
        code = generate_invite_code()
        exists = db.query(Org).filter(func.upper(Org.invite_code) == code).first()
        if not exists:
            return code


@router.get("", response_model=OrgListResponse)
def list_orgs(
    verified: bool | None = None,
    approved: bool | None = None,
    search: str | None = Query(None, description="Buscar por nome ou email"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrgListResponse:
    query = db.query(Org)

    if verified is not None:
        query = query.filter(Org.verified == verified)
    if approved is not None:
        query = query.filter(Org.approved == approved)
    if search:
        like = f"%{search.lower()}%"
        query = query.filter(
            or_(func.lower(Org.name).like(like), func.lower(Org.email).like(like))
        )

    total = query.count()
    orgs = (
        query.order_by(Org.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return OrgListResponse(orgs=orgs, total=total, page=page, page_size=page_size)


@router.post("", response_model=OrgResponse, status_code=status.HTTP_201_CREATED)
def create_org(
    data: OrgCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrgResponse:
    existing = db.query(Org).filter(func.lower(Org.email) == data.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado para outra ONG",
        )

    invite_code = _generate_unique_invite_code(db)

    org = Org(
        name=data.name,
        email=data.email,
        description=data.description,
        invite_code=invite_code,
        verified=False,
        approved=False,
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@router.get("/{org_id}", response_model=OrgResponse)
def get_org(
    org_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrgResponse:
    org = db.query(Org).filter(Org.id == org_id).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ONG não encontrada")
    return org


@router.put("/{org_id}", response_model=OrgResponse)
def update_org(
    org_id: int,
    data: OrgUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrgResponse:
    org = db.query(Org).filter(Org.id == org_id).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ONG não encontrada")

    update_data = data.model_dump(exclude_unset=True)

    if "email" in update_data and update_data["email"] != org.email:
        exists = (
            db.query(Org)
            .filter(func.lower(Org.email) == update_data["email"].lower(), Org.id != org.id)
            .first()
        )
        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já utilizado por outra ONG",
            )

    for field, value in update_data.items():
        setattr(org, field, value)

    db.commit()
    db.refresh(org)
    return org


@router.post("/validate-invite", response_model=ValidateInviteCodeResponse)
def validate_invite_code(
    payload: ValidateInviteCodeRequest,
    db: Session = Depends(get_db),
) -> ValidateInviteCodeResponse:
    org = (
        db.query(Org)
        .filter(func.upper(Org.invite_code) == payload.invite_code.upper())
        .first()
    )
    if not org:
        return ValidateInviteCodeResponse(valid=False)

    return ValidateInviteCodeResponse(valid=True, org_name=org.name, org_id=org.id)


@router.post("/{org_id}/regenerate-invite", response_model=OrgResponse)
def regenerate_invite_code(
    org_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrgResponse:
    org = db.query(Org).filter(Org.id == org_id).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ONG não encontrada")

    org.invite_code = _generate_unique_invite_code(db)
    db.commit()
    db.refresh(org)
    return org


@router.post("/resend-invite")
def resend_invite_email(
    payload: ResendInviteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    email_service: EmailService = Depends(get_email_service),
):
    org = db.query(Org).filter(Org.id == payload.org_id).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ONG não encontrada")

    try:
        send_invite_email(
            email_service,
            recipient=org.email,
            invite_code=org.invite_code,
            org_name=org.name,
        )
    except EmailNotConfiguredError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(exc)) from exc

    return {"message": "Convite enviado por email.", "org_email": org.email}


@router.post("/invite-by-email", response_model=InviteOrgByEmailResponse, status_code=status.HTTP_201_CREATED)
def invite_org_by_email(
    payload: InviteOrgByEmailRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    email_service: EmailService = Depends(get_email_service),
) -> InviteOrgByEmailResponse:
    """
    Cria uma nova ONG e envia automaticamente o email de convite.

    Este endpoint combina a criação da ONG com o envio do email de convite,
    simplificando o processo de convite de novas organizações.
    """
    # Verificar se email já está cadastrado
    existing = db.query(Org).filter(func.lower(Org.email) == payload.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado para outra ONG",
        )

    # Gerar código de convite único
    invite_code = _generate_unique_invite_code(db)

    # Criar a ONG
    org = Org(
        name=payload.name,
        email=payload.email,
        description=payload.description,
        invite_code=invite_code,
        verified=False,
        approved=False,
    )
    db.add(org)
    db.commit()
    db.refresh(org)

    # Enviar email de convite
    try:
        send_invite_email(
            email_service,
            recipient=org.email,
            invite_code=org.invite_code,
            org_name=org.name,
        )
        email_sent = True
        message = f"ONG criada e convite enviado para {org.email}"
    except EmailNotConfiguredError:
        email_sent = False
        message = f"ONG criada, mas email não configurado. Código de convite: {org.invite_code}"

    return InviteOrgByEmailResponse(
        org_id=org.id,
        org_name=org.name,
        org_email=org.email,
        invite_code=org.invite_code,
        message=message,
    )


@router.post("/{org_id}/verify-email", response_model=OrgResponse)
def verify_org_email(
    org_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrgResponse:
    org = db.query(Org).filter(Org.id == org_id).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ONG não encontrada")

    org.verified = True
    org.verified_at = datetime.utcnow()
    db.commit()
    db.refresh(org)
    return org


@router.post("/approve", response_model=OrgApprovalResponse)
def approve_org(
    payload: ApproveOrgRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    email_service: EmailService = Depends(get_email_service),
) -> OrgApprovalResponse:
    org = db.query(Org).filter(Org.id == payload.org_id).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ONG não encontrada")

    org.approved = payload.approved
    org.approved_by_id = current_user.id
    org.approved_at = datetime.utcnow()
    if payload.approved:
        org.verified = True
        org.verified_at = datetime.utcnow()

    db.commit()
    db.refresh(org)

    message = (
        "ONG aprovada com sucesso." if payload.approved else f"ONG rejeitada: {payload.reason or 'sem motivo informado'}"
    )
    try:
        send_org_validation_email(
            email_service,
            recipient=org.email,
            org_name=org.name,
            approval_status=payload.approved,
            reason=payload.reason,
        )
    except EmailNotConfiguredError:
        pass

    return OrgApprovalResponse(
        org_id=org.id,
        approved=org.approved,
        approved_by_id=current_user.id,
        approved_at=org.approved_at,
        message=message,
    )
