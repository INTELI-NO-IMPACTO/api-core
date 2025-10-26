from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..db import get_db
from ..dependencies import require_admin
from ..models.donation import Donation, DonationLedger, DonationStatus
from ..models.org import Org
from ..schemas.donation import (
    DonationCreate,
    DonationLedgerEntry,
    DonationLedgerResponse,
    DonationListResponse,
    DonationResponse,
    DonationWithLedgerResponse,
)

router = APIRouter(prefix="/donations", tags=["donations"])


def _ensure_org_exists(db: Session, org_id: int) -> Org:
    org = db.query(Org).filter(Org.id == org_id).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ONG não encontrada")
    return org


def _add_ledger_entry(
    db: Session,
    *,
    donation: Donation,
    entry_type: str,
    description: str,
    amount: float | None = None,
    metadata: str | None = None,
) -> DonationLedger:
    ledger = DonationLedger(
        donation_id=donation.id,
        entry_type=entry_type,
        description=description,
        amount=Decimal(str(amount)) if amount is not None else None,
        ledger_metadata=metadata,
    )
    db.add(ledger)
    return ledger


@router.post("", response_model=DonationResponse, status_code=status.HTTP_201_CREATED)
def create_donation(data: DonationCreate, db: Session = Depends(get_db)) -> DonationResponse:
    _ensure_org_exists(db, data.org_id)

    donation = Donation(
        donor_name=data.donor_name,
        donor_email=data.donor_email,
        org_id=data.org_id,
        amount=Decimal(str(data.amount)),
        currency="BRL",
        status=DonationStatus.COMPLETED,
        message=data.message,
        people_impacted=data.people_impacted,
        completed_at=datetime.utcnow(),
    )
    db.add(donation)
    db.flush()

    _add_ledger_entry(
        db,
        donation=donation,
        entry_type="created",
        description="Doação criada via mock gateway.",
        amount=data.amount,
    )
    _add_ledger_entry(
        db,
        donation=donation,
        entry_type="completed",
        description="Doação marcada como concluída automaticamente.",
        amount=data.amount,
    )

    db.commit()
    db.refresh(donation)
    return donation


@router.get("", response_model=DonationListResponse)
def list_donations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    org_id: int | None = None,
    status_filter: DonationStatus | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
) -> DonationListResponse:
    query = db.query(Donation)

    if org_id:
        query = query.filter(Donation.org_id == org_id)
    if status_filter:
        query = query.filter(Donation.status == status_filter)

    total = query.count()
    total_amount = query.with_entities(func.coalesce(func.sum(Donation.amount), 0)).scalar() or Decimal("0")

    donations = (
        query.order_by(Donation.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return DonationListResponse(
        donations=donations,
        total=total,
        total_amount=float(total_amount),
        page=page,
        page_size=page_size,
    )


@router.get("/{donation_id}", response_model=DonationWithLedgerResponse)
def get_donation(donation_id: int, db: Session = Depends(get_db)) -> DonationWithLedgerResponse:
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doação não encontrada")

    donation.ledger_entries  # Trigger lazy load if needed
    return donation


@router.post(
    "/{donation_id}/ledger",
    response_model=DonationLedgerResponse,
    status_code=status.HTTP_201_CREATED,
)
def append_ledger_entry(
    donation_id: int,
    entry: DonationLedgerEntry,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
) -> DonationLedgerResponse:
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doação não encontrada")

    ledger_entry = _add_ledger_entry(
        db,
        donation=donation,
        entry_type=entry.entry_type,
        description=entry.description,
        amount=entry.amount,
        metadata=entry.ledger_metadata,
    )
    db.commit()
    db.refresh(ledger_entry)
    return ledger_entry
