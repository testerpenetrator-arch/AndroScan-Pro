from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.identity import Role, User

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
Base.metadata.create_all(engine)


def override_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_db

with TestingSession() as db:
    for name, description in [
        ("ADMIN", "Administrador"),
        ("ANALYST", "Analista"),
        ("DEVELOPER", "Desarrollador"),
        ("IT_MANAGER", "Gestor TI"),
    ]:
        db.add(Role(name=name, description=description))
    db.add(User(email="admin@androscan.dev", full_name="Administrador de pruebas", password_hash=hash_password("Password123!")))
    db.commit()


def test_login_returns_bearer_token():
    client = TestClient(app)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@androscan.dev", "password": "Password123!"},
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_protected_endpoint_requires_authentication():
    client = TestClient(app)
    response = client.get("/api/v1/organizations")
    assert response.status_code == 401


def test_invalid_credentials_are_rejected():
    client = TestClient(app)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@androscan.dev", "password": "incorrect-password"},
    )
    assert response.status_code == 401


def test_organization_creation_and_tenant_membership():
    client = TestClient(app)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@androscan.dev", "password": "Password123!"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/api/v1/organizations",
        json={"name": "Empresa A", "slug": "empresa-a"},
        headers=headers,
    )
    assert created.status_code == 201
    organization_id = created.json()["id"]

    user = client.post(
        f"/api/v1/organizations/{organization_id}/users",
        json={
            "email": "analyst@androscan.dev",
            "full_name": "Analista A",
            "password": "Analyst123!",
        },
        headers=headers,
    )
    assert user.status_code == 201

    analyst_login = client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@androscan.dev", "password": "Analyst123!"},
    )
    analyst_headers = {"Authorization": f"Bearer {analyst_login.json()['access_token']}"}

    own_orgs = client.get("/api/v1/organizations", headers=analyst_headers)
    assert own_orgs.status_code == 200
    assert len(own_orgs.json()) == 1
    assert own_orgs.json()[0]["id"] == organization_id

    denied = client.get(f"/api/v1/organizations/{organization_id}/users", headers=analyst_headers)
    assert denied.status_code == 403
