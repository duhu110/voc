from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from backend_api.auth import hash_password, public_user, require_admin
from backend_api.db_utils import jsonable_row, pagination
from backend_api.schemas import PasswordResetRequest, UserCreateRequest, UserPatchRequest
from voc_agent.core.db import get_engine

router = APIRouter(prefix="/users", tags=["users"])


def _fetch_user(user_id: int) -> dict[str, Any] | None:
    with get_engine().connect() as conn:
        row = conn.execute(text("select * from app_users where id = :id"), {"id": user_id}).mappings().first()
    return jsonable_row(row) if row else None


@router.get("")
async def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    q: str | None = Query(default=None),
    role: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    _: dict = Depends(require_admin),
) -> dict:
    limit, offset = pagination(page, page_size)
    clauses = ["1 = 1"]
    params: dict[str, Any] = {"limit": limit, "offset": offset}
    if q:
        clauses.append("(username ilike :q or display_name ilike :q)")
        params["q"] = f"%{q}%"
    if role:
        clauses.append("role = :role")
        params["role"] = role
    if status_filter:
        clauses.append("status = :status")
        params["status"] = status_filter
    where_sql = " and ".join(clauses)

    with get_engine().connect() as conn:
        rows = conn.execute(
            text(
                f"""
                select id, username, display_name, role, status, token_version,
                       last_login_at, created_at, updated_at
                from app_users
                where {where_sql}
                order by id desc
                limit :limit offset :offset
                """
            ),
            params,
        ).mappings().all()
        total = conn.execute(text(f"select count(*) from app_users where {where_sql}"), params).scalar_one()

    return {
        "status": "success",
        "items": [jsonable_row(row) for row in rows],
        "page": page,
        "page_size": limit,
        "total": total,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(request_body: UserCreateRequest, _: dict = Depends(require_admin)) -> dict:
    try:
        with get_engine().begin() as conn:
            row = conn.execute(
                text(
                    """
                    insert into app_users (username, display_name, password_hash, role, status)
                    values (:username, :display_name, :password_hash, :role, :status)
                    returning *
                    """
                ),
                {
                    "username": request_body.username,
                    "display_name": request_body.display_name,
                    "password_hash": hash_password(request_body.password),
                    "role": request_body.role,
                    "status": request_body.status,
                },
            ).mappings().one()
    except IntegrityError as exc:
        if "app_users_username_key" in str(exc) or "duplicate key" in str(exc):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists") from exc
        raise
    return {"status": "success", "user": public_user(jsonable_row(row))}


@router.get("/{user_id}")
async def get_user(user_id: int, _: dict = Depends(require_admin)) -> dict:
    user = _fetch_user(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"status": "success", "user": public_user(user)}


@router.patch("/{user_id}")
async def patch_user(user_id: int, request_body: UserPatchRequest, _: dict = Depends(require_admin)) -> dict:
    values = request_body.model_dump(exclude_unset=True)
    if not values:
        user = _fetch_user(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return {"status": "success", "user": public_user(user)}

    set_parts = [f"{key} = :{key}" for key in values]
    set_parts.append("updated_at = now()")
    if values.get("status") and values["status"] != "active":
        set_parts.append("token_version = token_version + 1")
    values["id"] = user_id

    with get_engine().begin() as conn:
        row = conn.execute(
            text(f"update app_users set {', '.join(set_parts)} where id = :id returning *"),
            values,
        ).mappings().first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"status": "success", "user": public_user(jsonable_row(row))}


@router.post("/{user_id}/reset-password")
async def reset_password(
    user_id: int,
    request_body: PasswordResetRequest,
    _: dict = Depends(require_admin),
) -> dict:
    with get_engine().begin() as conn:
        row = conn.execute(
            text(
                """
                update app_users
                set password_hash = :password_hash,
                    token_version = token_version + 1,
                    updated_at = now()
                where id = :id
                returning *
                """
            ),
            {"id": user_id, "password_hash": hash_password(request_body.password)},
        ).mappings().first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"status": "success", "user": public_user(jsonable_row(row))}
