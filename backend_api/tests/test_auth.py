from __future__ import annotations

from dataclasses import dataclass

from fastapi.testclient import TestClient

from backend_api import auth
from backend_api.main import create_app
from backend_api.routes import auth as auth_routes


@dataclass(frozen=True)
class DummySettings:
    auth_jwt_secret: str = "test-secret-with-at-least-32-bytes"
    auth_token_expire_minutes: int = 30


def test_password_hash_roundtrip() -> None:
    password_hash = auth.hash_password("correct-password")

    assert auth.verify_password("correct-password", password_hash)
    assert not auth.verify_password("wrong-password", password_hash)


def test_access_token_roundtrip(monkeypatch) -> None:
    monkeypatch.setattr(auth, "get_settings", lambda: DummySettings())
    token, expires_in = auth.create_access_token(
        {"id": 7, "username": "admin", "role": "admin", "token_version": 3}
    )

    payload = auth.decode_access_token(token)

    assert expires_in == 1800
    assert payload["sub"] == "7"
    assert payload["username"] == "admin"
    assert payload["role"] == "admin"
    assert payload["token_version"] == 3


def test_me_route_uses_current_user_dependency_override() -> None:
    app = create_app()

    async def fake_current_user() -> dict:
        return {
            "id": 1,
            "username": "admin",
            "display_name": "管理员",
            "role": "admin",
            "status": "active",
            "last_login_at": None,
            "created_at": None,
            "updated_at": None,
        }

    app.dependency_overrides[auth_routes.get_current_user] = fake_current_user
    client = TestClient(app)

    response = client.get("/auth/me")

    assert response.status_code == 200
    assert response.json()["user"]["username"] == "admin"


def test_login_route_returns_bearer_token(monkeypatch) -> None:
    user = {
        "id": 1,
        "username": "admin",
        "display_name": "管理员",
        "password_hash": auth.hash_password("correct-password"),
        "role": "admin",
        "status": "active",
        "token_version": 1,
        "last_login_at": None,
        "created_at": None,
        "updated_at": None,
    }

    class FakeResult:
        def mappings(self):
            return self

        def first(self):
            return user

    class FakeConnection:
        def execute(self, *args, **kwargs):
            return FakeResult()

    class FakeEngine:
        def begin(self):
            return self

        def __enter__(self):
            return FakeConnection()

        def __exit__(self, *args):
            return False

    monkeypatch.setattr(auth_routes, "fetch_user_by_username", lambda username: user)
    monkeypatch.setattr(auth_routes, "record_login_event", lambda **kwargs: None)
    monkeypatch.setattr(auth_routes, "create_access_token", lambda user: ("token-1", 3600))
    monkeypatch.setattr(auth_routes, "get_engine", lambda: FakeEngine())

    client = TestClient(create_app())
    response = client.post("/auth/login", json={"username": "admin", "password": "correct-password"})

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"] == "token-1"
    assert body["token_type"] == "bearer"
    assert body["user"]["username"] == "admin"
