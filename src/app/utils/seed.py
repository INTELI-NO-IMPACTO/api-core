from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Iterable

from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..models import (
    Donation,
    DonationLedger,
    DonationStatus,
    Org,
    Role,
    User,
)
from ..security import generate_invite_code, hash_password


def _get_or_create(
    session: Session,
    model,
    defaults: dict | None = None,
    **lookup,
):
    instance = session.query(model).filter_by(**lookup).first()
    if instance:
        return instance, False

    params = {**lookup, **(defaults or {})}
    instance = model(**params)
    session.add(instance)
    session.flush()
    return instance, True


def seed_orgs(session: Session) -> list[Org]:
    org_specs = [
        {
            "name": "Instituto Impacto Social",
            "email": "contato@impactosocial.org",
            "description": "Capacitação profissional para jovens em situação de vulnerabilidade.",
        },
        {
            "name": "Rede Saúde para Todos",
            "email": "info@saudeparatodos.org",
            "description": "Rede de clínicas itinerantes com foco em atendimento feminino.",
        },
        {
            "name": "Educação em Movimento",
            "email": "parcerias@educamov.org",
            "description": "Bibliotecas móveis e reforço escolar em comunidades ribeirinhas.",
        },
    ]

    orgs: list[Org] = []
    for spec in org_specs:
        defaults = {
            "description": spec["description"],
            "invite_code": generate_invite_code(),
            "verified": True,
            "approved": True,
            "approved_by_id": None,
            "approved_at": datetime.utcnow(),
            "verified_at": datetime.utcnow(),
        }
        org, created = _get_or_create(
            session,
            Org,
            defaults=defaults,
            name=spec["name"],
            email=spec["email"],
        )
        if created:
            print(f"[seed] ONG criada: {org.name}")
        orgs.append(org)
    return orgs


def seed_users(session: Session, orgs: Iterable[Org]) -> dict[str, User]:
    """Cria usuários (admin, assistentes e beneficiários)."""
    users: dict[str, User] = {}

    admin, created = _get_or_create(
        session,
        User,
        defaults={
            "password_hash": hash_password("admin123"),
            "name": "Admin Geral",
            "role": Role.ADMIN,
            "is_active": True,
        },
        email="admin@meunomegov.org",
    )
    if created:
        print("[seed] Usuário admin criado: admin@meunomegov.org (senha: admin123)")
    users["admin"] = admin

    for idx, org in enumerate(orgs, start=1):
        assist_email = f"assistente{idx}@{org.email.split('@')[-1]}"
        assistente, created = _get_or_create(
            session,
            User,
            defaults={
                "password_hash": hash_password("assist123"),
                "name": f"Assistente {idx}",
                "role": Role.ASSISTENTE,
                "org_id": org.id,
                "is_active": True,
            },
            email=assist_email,
        )
        if created:
            print(f"[seed] Assistente criado: {assist_email} (senha: assist123)")
        users[f"assistente_{idx}"] = assistente

        for ben_idx in range(1, 3):
            benef_email = f"beneficiario{idx}{ben_idx}@{org.email.split('@')[-1]}"
            beneficiario, created = _get_or_create(
                session,
                User,
                defaults={
                    "password_hash": hash_password("benef123"),
                    "name": f"Beneficiário {idx}-{ben_idx}",
                    "role": Role.BENEFICIARIO,
                    "org_id": org.id,
                    "assistente_id": assistente.id,
                    "is_active": True,
                },
                email=benef_email,
            )
            if created:
                print(f"[seed] Beneficiário criado: {benef_email} (senha: benef123)")
            users[f"beneficiario_{idx}_{ben_idx}"] = beneficiario

    return users


def seed_donations(session: Session, orgs: Iterable[Org]) -> None:
    """Cria doações mock e respectivas entradas no ledger."""
    mock_donations = [
        {
            "org": orgs[0],
            "donor_name": "Maria Oliveira",
            "donor_email": "maria@example.com",
            "amount": Decimal("250.00"),
            "message": "Feliz em apoiar o programa de formação.",
            "people_impacted": 5,
            "days_ago": 2,
        },
        {
            "org": orgs[0],
            "donor_name": "Anônimo",
            "donor_email": None,
            "amount": Decimal("150.00"),
            "message": None,
            "people_impacted": 3,
            "days_ago": 10,
        },
        {
            "org": orgs[1],
            "donor_name": "Empresa Solidária",
            "donor_email": "social@empresa.com",
            "amount": Decimal("1200.00"),
            "message": "Parceria para ampliar atendimentos clínicos.",
            "people_impacted": 20,
            "days_ago": 5,
        },
        {
            "org": orgs[2],
            "donor_name": "Coletivo Leitores",
            "donor_email": "contato@leitores.org",
            "amount": Decimal("600.00"),
            "message": "Livros e tablets para comunidades ribeirinhas.",
            "people_impacted": 12,
            "days_ago": 1,
        },
    ]

    for spec in mock_donations:
        donation = (
            session.query(Donation)
            .filter(
                Donation.donor_name == spec["donor_name"],
                Donation.org_id == spec["org"].id,
                Donation.amount == spec["amount"],
            )
            .first()
        )
        if donation:
            continue

        donation = Donation(
            donor_name=spec["donor_name"],
            donor_email=spec["donor_email"],
            org_id=spec["org"].id,
            amount=spec["amount"],
            currency="BRL",
            status=DonationStatus.COMPLETED,
            message=spec["message"],
            people_impacted=spec["people_impacted"],
            created_at=datetime.utcnow() - timedelta(days=spec["days_ago"]),
            completed_at=datetime.utcnow() - timedelta(days=spec["days_ago"]),
        )
        session.add(donation)
        session.flush()

        ledger_entries = [
            DonationLedger(
                donation_id=donation.id,
                entry_type="created",
                description="Doação registrada via seed.",
                amount=spec["amount"],
            ),
            DonationLedger(
                donation_id=donation.id,
                entry_type="completed",
                description="Doação liberada para a ONG.",
                amount=spec["amount"],
            ),
        ]
        session.add_all(ledger_entries)
        print(
            f"[seed] Doação registrada ({spec['org'].name}): "
            f"{spec['donor_name']} → R$ {spec['amount']}"
        )


def run_seed() -> None:
    session = SessionLocal()
    try:
        orgs = seed_orgs(session)
        seed_users(session, orgs)
        seed_donations(session, orgs)
        session.commit()
        print("[seed] Dados de exemplo para landing page criados com sucesso.")
    except Exception as exc:
        session.rollback()
        print(f"[seed] ERRO: {exc}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    run_seed()
