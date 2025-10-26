from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime


# =============== Base Schemas ===============

class OrgBase(BaseModel):
    name: str
    email: EmailStr
    description: str | None = None


class OrgCreate(OrgBase):
    """Schema para criar ONG - gera invite_code automaticamente"""
    pass


class OrgUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    description: str | None = None


class OrgResponse(OrgBase):
    id: int
    invite_code: str
    verified: bool
    approved: bool
    approved_by_id: int | None
    created_at: datetime
    updated_at: datetime
    verified_at: datetime | None
    approved_at: datetime | None

    class Config:
        from_attributes = True


# =============== Invite System ===============

class ValidateInviteCodeRequest(BaseModel):
    """Request para validar código de convite"""
    invite_code: str

    @field_validator('invite_code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError('Código de convite inválido')
        return v.upper()


class ValidateInviteCodeResponse(BaseModel):
    valid: bool
    org_name: str | None = None
    org_id: int | None = None


class ResendInviteRequest(BaseModel):
    """Request para reenviar email de convite"""
    org_id: int


class InviteOrgByEmailRequest(BaseModel):
    """Request para criar ONG e enviar convite por email"""
    email: EmailStr
    name: str
    description: str | None = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if len(v.strip()) < 3:
            raise ValueError('Nome deve ter no mínimo 3 caracteres')
        return v.strip()


class InviteOrgByEmailResponse(BaseModel):
    """Response de convite enviado"""
    org_id: int
    org_name: str
    org_email: str
    invite_code: str
    message: str


# =============== Approval System ===============

class ApproveOrgRequest(BaseModel):
    """Request para aprovar ONG (admin only)"""
    org_id: int
    approved: bool  # True = aprovar, False = rejeitar
    reason: str | None = None  # Razão da rejeição


class OrgApprovalResponse(BaseModel):
    org_id: int
    approved: bool
    approved_by_id: int
    approved_at: datetime
    message: str


# =============== List/Filter Schemas ===============

class OrgListResponse(BaseModel):
    orgs: list[OrgResponse]
    total: int
    page: int
    page_size: int


class OrgFilterParams(BaseModel):
    """Parâmetros de filtro para listagem de ONGs"""
    verified: bool | None = None
    approved: bool | None = None
    search: str | None = None  # Busca por nome ou email
    page: int = 1
    page_size: int = 20

    @field_validator('page')
    @classmethod
    def validate_page(cls, v: int) -> int:
        if v < 1:
            raise ValueError('Página deve ser maior que 0')
        return v

    @field_validator('page_size')
    @classmethod
    def validate_page_size(cls, v: int) -> int:
        if v < 1 or v > 100:
            raise ValueError('page_size deve estar entre 1 e 100')
        return v


# =============== Statistics ===============

class OrgStatsResponse(BaseModel):
    """Estatísticas de uma ONG"""
    org_id: int
    org_name: str
    total_assistentes: int
    total_beneficiarios: int
    total_donations: int
    total_amount_received: float
    people_impacted: int
