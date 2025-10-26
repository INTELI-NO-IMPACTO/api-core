from http import HTTPStatus

from src.app.models.user import Role, User


def test_assistente_cria_beneficiario(client, create_user, auth_header):
    assistente = create_user(email="assistente@example.com", role=Role.ASSISTENTE)
    payload = {
        "email": "beneficiario@example.com",
        "name": "Beneficiário Teste",
        "social_name": "Ben Teste",
        "password": "senha123",
        "assistente_id": assistente.id,
    }

    response = client.post(
        "/beneficiarios",
        json=payload,
        headers=auth_header(assistente),
    )

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["assistente_id"] == assistente.id
    assert data["role"] == Role.BENEFICIARIO.value


def test_assistente_nao_cria_para_outro_assistente(client, create_user, auth_header):
    assistente = create_user(email="assistente@example.com", role=Role.ASSISTENTE)
    outro_assistente = create_user(email="assistente2@example.com", role=Role.ASSISTENTE)

    payload = {
        "email": "beneficiario2@example.com",
        "name": "Beneficiário Dois",
        "password": "senha123",
        "assistente_id": outro_assistente.id,
    }

    response = client.post(
        "/beneficiarios",
        json=payload,
        headers=auth_header(assistente),
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_listagem_filtra_por_assistente(client, create_user, auth_header, db_session):
    assistente = create_user(email="assistente@example.com", role=Role.ASSISTENTE)
    outro_assistente = create_user(email="assistente2@example.com", role=Role.ASSISTENTE)

    beneficiarios = [
        create_user(
            email=f"beneficiario{i}@example.com",
            role=Role.BENEFICIARIO,
            assistente_id=assistente.id,
        )
        for i in range(2)
    ]

    create_user(
        email="outrobeneficiario@example.com",
        role=Role.BENEFICIARIO,
        assistente_id=outro_assistente.id,
    )

    response_assistente = client.get(
        "/beneficiarios",
        headers=auth_header(assistente),
    )
    assert response_assistente.status_code == HTTPStatus.OK
    data_assistente = response_assistente.json()
    assert data_assistente["total"] == len(beneficiarios)
    assert all(item["assistente_id"] == assistente.id for item in data_assistente["users"])

    admin = create_user(email="admin@example.com", role=Role.ADMIN)
    response_admin = client.get(
        "/beneficiarios",
        headers=auth_header(admin),
    )
    assert response_admin.status_code == HTTPStatus.OK
    data_admin = response_admin.json()
    assert data_admin["total"] == 3


def test_admin_atualiza_beneficiario(client, create_user, auth_header):
    assistente = create_user(email="assistente@example.com", role=Role.ASSISTENTE)
    beneficiario = create_user(
        email="beneficiario@example.com",
        role=Role.BENEFICIARIO,
        assistente_id=assistente.id,
    )
    admin = create_user(email="admin@example.com", role=Role.ADMIN)

    payload = {
        "name": "Beneficiário Atualizado",
        "assistente_id": None,
        "is_active": False,
    }

    response = client.put(
        f"/beneficiarios/{beneficiario.id}",
        json=payload,
        headers=auth_header(admin),
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["assistente_id"] is None
    assert data["is_active"] is False


def test_admin_vincula_beneficiario(client, create_user, auth_header):
    admin = create_user(email="admin@example.com", role=Role.ADMIN)
    assistente = create_user(email="assistente@example.com", role=Role.ASSISTENTE)
    beneficiario = create_user(
        email="beneficiario@example.com",
        role=Role.BENEFICIARIO,
        assistente_id=None,
    )

    response = client.post(
        "/beneficiarios/vincular",
        json={"beneficiario_id": beneficiario.id, "assistente_id": assistente.id},
        headers=auth_header(admin),
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["assistente_id"] == assistente.id


def test_assistente_nao_vincula_para_outro(client, create_user, auth_header):
    assistente = create_user(email="assistente@example.com", role=Role.ASSISTENTE)
    outro_assistente = create_user(email="assistente2@example.com", role=Role.ASSISTENTE)
    beneficiario = create_user(
        email="beneficiario@example.com",
        role=Role.BENEFICIARIO,
        assistente_id=assistente.id,
    )

    response = client.post(
        "/beneficiarios/vincular",
        json={"beneficiario_id": beneficiario.id, "assistente_id": outro_assistente.id},
        headers=auth_header(assistente),
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
