from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from ..models.donation import DonationStatus


# =============== Base Schemas ===============

class DonationBase(BaseModel):
    donor_name: str
    donor_email: EmailStr | None = None
    org_id: int
    amount: float
    message: str | None = None
    people_impacted: int = 1

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Valor deve ser maior que zero')
        if v > 1000000:
            raise ValueError('Valor muito alto')
        return round(v, 2)

    @field_validator('people_impacted')
    @classmethod
    def validate_people_impacted(cls, v: int) -> int:
        if v < 1:
            raise ValueError('Pessoas impactadas deve ser no mínimo 1')
        return v


class DonationCreate(DonationBase):
    """Schema para criar doação"""
    pass


class DonationResponse(DonationBase):
    id: int
    currency: str
    status: DonationStatus
    created_at: datetime
    completed_at: datetime | None

    class Config:
        from_attributes = True


# =============== Donation Ledger ===============

class DonationLedgerEntry(BaseModel):
    """Entrada no ledger de transparência"""
    entry_type: str  # "created", "completed", "allocated", "spent"
    description: str
    amount: float | None = None
    ledger_metadata: str | None = None


class DonationLedgerResponse(DonationLedgerEntry):
    id: int
    donation_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class DonationWithLedgerResponse(DonationResponse):
    """Doação completa com histórico de ledger"""
    ledger_entries: list[DonationLedgerResponse]


# =============== List/Filter Schemas ===============

class DonationListResponse(BaseModel):
    donations: list[DonationResponse]
    total: int
    total_amount: float
    page: int
    page_size: int


class DonationFilterParams(BaseModel):
    """Parâmetros de filtro para listagem de doações"""
    org_id: int | None = None
    status: DonationStatus | None = None
    donor_email: str | None = None
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

class DonationStatsResponse(BaseModel):
    """Estatísticas gerais de doações (para landing page)"""
    total_donations: int
    total_amount: float
    total_orgs: int
    total_people_impacted: int
    recent_donations: list[DonationResponse]  # Últimas 5


class OrgDonationStatsResponse(BaseModel):
    """Estatísticas de doações de uma ONG específica"""
    org_id: int
    org_name: str
    total_donations: int
    total_amount: float
    people_impacted: int
    last_donation_at: datetime | None
