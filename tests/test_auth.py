import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

TEST_DB_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    return TestClient(app)


def test_health_and_root(client):
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert res_root.json()["status"] == "online"

    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"


def test_register_and_login_flow(client):
    # 1. Register regular user
    reg_payload = {
        "email": "alice@example.com",
        "username": "alice",
        "password": "Password123!",
        "full_name": "Alice Smith",
        "role": "user"
    }
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert reg_data["username"] == "alice"
    assert reg_data["role"] == "user"

    # 2. Login with valid credentials
    login_payload = {
        "username_or_email": "alice",
        "password": "Password123!"
    }
    login_res = client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    tokens = login_res.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"

    # 3. Access protected /users/me
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    me_res = client.get("/api/v1/users/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["username"] == "alice"


def test_duplicate_registration_prevented(client):
    payload = {
        "email": "duplicate@example.com",
        "username": "duplicate_user",
        "password": "SecurePassword1!"
    }
    res1 = client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 409


def test_invalid_login_credentials(client):
    # Non-existent user
    res = client.post("/api/v1/auth/login", json={"username_or_email": "fake", "password": "wrong"})
    assert res.status_code == 401


def test_unauthorized_access_without_token(client):
    res = client.get("/api/v1/users/me")
    assert res.status_code == 401


def test_role_based_access_control(client):
    # 1. Register standard user
    client.post("/api/v1/auth/register", json={
        "email": "user@example.com",
        "username": "standard_user",
        "password": "Password123!",
        "role": "user"
    })
    user_token = client.post("/api/v1/auth/login", json={
        "username_or_email": "standard_user",
        "password": "Password123!"
    }).json()["access_token"]

    # 2. Register admin user
    client.post("/api/v1/auth/register", json={
        "email": "admin@example.com",
        "username": "system_admin",
        "password": "AdminPassword123!",
        "role": "admin"
    })
    admin_token = client.post("/api/v1/auth/login", json={
        "username_or_email": "system_admin",
        "password": "AdminPassword123!"
    }).json()["access_token"]

    # Standard user trying to access admin endpoint -> 403 Forbidden
    forbidden_res = client.get(
        "/api/v1/admin/stats",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert forbidden_res.status_code == 403

    # Admin accessing admin endpoint -> 200 OK
    admin_res = client.get(
        "/api/v1/admin/stats",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert admin_res.status_code == 200
    stats = admin_res.json()
    assert stats["total_registered_users"] == 2
    assert stats["role_breakdown"]["admin"] == 1


def test_refresh_token_rotation(client):
    client.post("/api/v1/auth/register", json={
        "email": "rotate@example.com",
        "username": "rotator",
        "password": "Password123!"
    })
    login_data = client.post("/api/v1/auth/login", json={
        "username_or_email": "rotator",
        "password": "Password123!"
    }).json()

    first_refresh = login_data["refresh_token"]

    # Rotate refresh token
    refresh_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": first_refresh}
    )
    assert refresh_res.status_code == 200
    new_tokens = refresh_res.json()
    assert new_tokens["refresh_token"] != first_refresh

    # Re-using the old refresh token must be rejected (revoked)
    replay_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": first_refresh}
    )
    assert replay_res.status_code == 401
