from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Numeric, Text, DateTime, ForeignKey, func, Enum
from ..db import Base
from datetime import datetime
import enum

class DonationStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class Donation(Base):
    __tablename__ = "donations"
    id: Mapped[int] = mapped_column(primary_key=True)

    # Doador (pode ser anônimo)
    donor_name: Mapped[str] = mapped_column(String(255))
    donor_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ONG beneficiada
    org_id: Mapped[int] = mapped_column(ForeignKey("orgs.id"), index=True)

    # Valor da doação
    amount: Mapped[float] = mapped_column(Numeric(10, 2))
    currency: Mapped[str] = mapped_column(String(3), default="BRL")

    # Status e processamento
    status: Mapped[DonationStatus] = mapped_column(default=DonationStatus.PENDING)

    # Informações adicionais
    message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Impacto estimado (número de pessoas)
    people_impacted: Mapped[int | None] = mapped_column(nullable=True, default=1)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    org = relationship("Org", back_populates="donations")
    ledger_entries = relationship("DonationLedger", back_populates="donation", cascade="all, delete-orphan")


class DonationLedger(Base):
    """Registro de transparência de doações (immutable ledger)"""
    __tablename__ = "donation_ledger"
    id: Mapped[int] = mapped_column(primary_key=True)

    donation_id: Mapped[int] = mapped_column(ForeignKey("donations.id"), index=True)

    # Tipo de registro
    entry_type: Mapped[str] = mapped_column(String(50))  # "created", "completed", "allocated", "spent"

    # Descrição do registro
    description: Mapped[str] = mapped_column(Text)

    # Valor envolvido (se aplicável)
    amount: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)

    # Metadados (JSON string)
    ledger_metadata: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamp (imutável)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    donation = relationship("Donation", back_populates="ledger_entries")
