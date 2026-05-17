from __future__ import annotations

import base64
import hashlib
import hmac
import os
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import text

from backend_api.db_utils import jsonable_row
from voc_agent.core.config import get_settings
from voc_agent.core.db import get_engine

PASSWORD_ALGORITHM = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 260_000
JWT_ALGORITHM = "HS256"

bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str, *, salt: str | None = None, iterations: int = PASSWORD_ITERATIONS) -> str:
    if not password:
        raise ValueError("password must not be empty")
    raw_salt = salt or base64.urlsafe_b64encode(os.urandom(18)).decode("ascii").rstrip("=")
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), raw_salt.encode("utf-8"), iterations)
    encoded = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return f"{PASSWORD_ALGORITHM}${iterations}${raw_salt}${encoded}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations_raw, salt, expected = password_hash.split("$", 3)
        iterations = int(iterations_raw)
    except ValueError:
        return False
    if algorithm != PASSWORD_ALGORITHM:
        return False
    actual = hash_password(password, salt=salt, iterations=iterations).split("$", 3)[3]
    return hmac.compare_digest(actual, expected)


def create_access_token(user: dict[str, Any]) -> tuple[str, int]:
    settings = get_settings()
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.auth_token_expire_minutes)
    payload = {
        "sub": str(user["id"]),
        "username": user["username"],
        "role": user["role"],
        "token_version": int(user["token_version"]),
        "exp": expires_at,
        "iat": datetime.now(UTC),
    }
    token = jwt.encode(payload, settings.auth_jwt_secret, algorithm=JWT_ALGORITHM)
    return token, settings.auth_token_expire_minutes * 60


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, get_settings().auth_jwt_secret, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    return payload


def fetch_user_by_username(username: str) -> dict[str, Any] | None:
    with get_engine().connect() as conn:
        row = conn.execute(
            text("select * from app_users where username = :username"),
            {"username": username},
        ).mappings().first()
    return jsonable_row(row) if row else None


def fetch_user_by_id(user_id: str | int) -> dict[str, Any] | None:
    with get_engine().connect() as conn:
        row = conn.execute(
            text("select * from app_users where id = :id"),
            {"id": int(user_id)},
        ).mappings().first()
    return jsonable_row(row) if row else None


def public_user(user: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": user["id"],
        "username": user["username"],
        "display_name": user.get("display_name"),
        "role": user["role"],
        "status": user["status"],
        "last_login_at": user.get("last_login_at"),
        "created_at": user.get("created_at"),
        "updated_at": user.get("updated_at"),
    }


def record_login_event(
    *,
    username: str,
    user_id: int | None,
    success: bool,
    failure_reason: str | None,
    request: Request | None,
) -> None:
    client_host = request.client.host if request and request.client else None
    user_agent = request.headers.get("user-agent") if request else None
    with get_engine().begin() as conn:
        conn.execute(
            text(
                """
                insert into app_user_login_events (
                    user_id, username, success, failure_reason, client_host, user_agent
                )
                values (:user_id, :username, :success, :failure_reason, :client_host, :user_agent)
                """
            ),
            {
                "user_id": user_id,
                "username": username,
                "success": success,
                "failure_reason": failure_reason,
                "client_host": client_host,
                "user_agent": user_agent,
            },
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, Any]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    payload = decode_access_token(credentials.credentials)
    user = fetch_user_by_id(payload.get("sub", "0"))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if user["status"] != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not active")
    if int(user["token_version"]) != int(payload.get("token_version", 0)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")
    return user


async def require_admin(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return current_user
