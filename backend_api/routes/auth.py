from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import text

from backend_api.auth import (
    create_access_token,
    fetch_user_by_username,
    get_current_user,
    hash_password,
    public_user,
    record_login_event,
    require_admin,
    verify_password,
)
from backend_api.schemas import ChangePasswordRequest, LoginRequest
from voc_agent.core.db import get_engine

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(request_body: LoginRequest, request: Request) -> dict:
    user = fetch_user_by_username(request_body.username)
    if user is None:
        record_login_event(
            username=request_body.username,
            user_id=None,
            success=False,
            failure_reason="user_not_found",
            request=request,
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    if user["status"] != "active":
        record_login_event(
            username=user["username"],
            user_id=int(user["id"]),
            success=False,
            failure_reason=f"user_{user['status']}",
            request=request,
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not active")
    if not verify_password(request_body.password, user["password_hash"]):
        record_login_event(
            username=user["username"],
            user_id=int(user["id"]),
            success=False,
            failure_reason="bad_password",
            request=request,
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    token, expires_in = create_access_token(user)
    with get_engine().begin() as conn:
        conn.execute(
            text("update app_users set last_login_at = now(), updated_at = now() where id = :id"),
            {"id": user["id"]},
        )
    record_login_event(username=user["username"], user_id=int(user["id"]), success=True, failure_reason=None, request=request)
    fresh_user = fetch_user_by_username(user["username"]) or user
    return {
        "status": "success",
        "access_token": token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "user": public_user(fresh_user),
    }


@router.get("/me")
async def me(current_user: dict = Depends(get_current_user)) -> dict:
    return {"status": "success", "user": public_user(current_user)}


@router.post("/change-password")
async def change_password(
    request_body: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
) -> dict:
    if not verify_password(request_body.current_password, current_user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    with get_engine().begin() as conn:
        conn.execute(
            text(
                """
                update app_users
                set password_hash = :password_hash,
                    token_version = token_version + 1,
                    updated_at = now()
                where id = :id
                """
            ),
            {"id": current_user["id"], "password_hash": hash_password(request_body.new_password)},
        )
    return {"status": "success"}


@router.get("/admin-check")
async def admin_check(current_user: dict = Depends(require_admin)) -> dict:
    return {"status": "success", "user": public_user(current_user)}
