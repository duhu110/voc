from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from backend_api.rag_client import RagClient
from voc_agent.core.db import get_engine

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    database_status = "ok"
    database_detail: dict[str, str] = {}
    try:
        with get_engine().connect() as conn:
            row = conn.execute(text("select current_database() as db, current_user as db_user")).mappings().first()
            database_detail = dict(row or {})
    except Exception as exc:  # pragma: no cover - defensive health endpoint
        database_status = "error"
        database_detail = {"error": str(exc)}

    rag_status = "ok"
    rag_detail: dict = {}
    try:
        rag_detail = await RagClient().health()
    except Exception as exc:  # pragma: no cover - network-dependent
        rag_status = "error"
        rag_detail = {"error": str(exc)}

    status = "ok" if database_status == "ok" and rag_status == "ok" else "degraded"
    return {
        "status": status,
        "database": {"status": database_status, **database_detail},
        "rag": {"status": rag_status, "detail": rag_detail},
    }

