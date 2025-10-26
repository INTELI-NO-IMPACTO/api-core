from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.donation import Donation, DonationStatus
from ..models.org import Org
from ..models.user import Role, User
from ..schemas.donation import DonationStatsResponse, OrgDonationStatsResponse
from ..schemas.org import OrgStatsResponse

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/landing", response_model=DonationStatsResponse)
def landing_metrics(db: Session = Depends(get_db)) -> DonationStatsResponse:
    donation_query = db.query(Donation).filter(Donation.status == DonationStatus.COMPLETED)

    total_amount = donation_query.with_entities(func.coalesce(func.sum(Donation.amount), 0)).scalar() or Decimal("0")
    total_donations = donation_query.count()
    total_people_impacted = (
        donation_query.with_entities(func.coalesce(func.sum(Donation.people_impacted), 0)).scalar() or 0
    )
    total_orgs = db.query(Org).filter(Org.approved == True).count()

    recent = (
        donation_query.order_by(Donation.created_at.desc())
        .limit(5)
        .all()
    )

    return DonationStatsResponse(
        total_donations=total_donations,
        total_amount=float(total_amount),
        total_orgs=total_orgs,
        total_people_impacted=int(total_people_impacted),
        recent_donations=recent,
    )


@router.get("/orgs/{org_id}", response_model=OrgDonationStatsResponse)
def org_donation_metrics(org_id: int, db: Session = Depends(get_db)) -> OrgDonationStatsResponse:
    org = db.query(Org).filter(Org.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="ONG não encontrada")

    donation_query = db.query(Donation).filter(Donation.org_id == org_id, Donation.status == DonationStatus.COMPLETED)

    total_amount = donation_query.with_entities(func.coalesce(func.sum(Donation.amount), 0)).scalar() or Decimal("0")
    total_donations = donation_query.count()
    people_impacted = (
        donation_query.with_entities(func.coalesce(func.sum(Donation.people_impacted), 0)).scalar() or 0
    )
    last_donation_at = (
        donation_query.with_entities(func.max(Donation.created_at))
        .scalar()
    )

    return OrgDonationStatsResponse(
        org_id=org.id,
        org_name=org.name,
        total_donations=total_donations,
        total_amount=float(total_amount),
        people_impacted=int(people_impacted),
        last_donation_at=last_donation_at,
    )


@router.get("/orgs/{org_id}/overview", response_model=OrgStatsResponse)
def org_overview_metrics(org_id: int, db: Session = Depends(get_db)) -> OrgStatsResponse:
    org = db.query(Org).filter(Org.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="ONG não encontrada")
    total_assistentes = (
        db.query(func.count(User.id))
        .filter(User.org_id == org_id, User.role == Role.ASSISTENTE)
        .scalar()
        or 0
    )
    total_beneficiarios = (
        db.query(func.count(User.id))
        .filter(User.org_id == org_id, User.role == Role.BENEFICIARIO)
        .scalar()
        or 0
    )

    donations_query = db.query(Donation).filter(Donation.org_id == org_id, Donation.status == DonationStatus.COMPLETED)
    total_amount = donations_query.with_entities(func.coalesce(func.sum(Donation.amount), 0)).scalar() or Decimal("0")
    total_donations = donations_query.count()
    people_impacted = (
        donations_query.with_entities(func.coalesce(func.sum(Donation.people_impacted), 0)).scalar() or 0
    )

    return OrgStatsResponse(
        org_id=org.id,
        org_name=org.name,
        total_assistentes=int(total_assistentes),
        total_beneficiarios=int(total_beneficiarios),
        total_donations=total_donations,
        total_amount_received=float(total_amount),
        people_impacted=int(people_impacted),
    )
