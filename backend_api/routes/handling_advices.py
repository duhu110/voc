from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from backend_api.db_utils import jsonable_row, pagination
from voc_agent.core.db import get_engine

router = APIRouter(prefix="/handling-advices", tags=["handling-advices"])

LIST_SQL = text(
    """
    select
      id, primary_leaf_code, primary_leaf_name, product_tag_code, product_tag_name,
      request_tag_code, request_tag_name, risk_tag_code, risk_tag_name,
      advice_title, advice_content, applicability_note, source_summary_count,
      latest_source_ticket_id, status, created_at, updated_at
    from converger_handling_advice
    where (cast(:status as varchar) is null or status = :status)
      and (cast(:primary_leaf_code as varchar) is null or primary_leaf_code = :primary_leaf_code)
      and (cast(:product_tag_code as varchar) is null or product_tag_code = :product_tag_code)
      and (cast(:request_tag_code as varchar) is null or request_tag_code = :request_tag_code)
      and (
        cast(:query as varchar) is null
        or advice_title ilike :query_like
        or advice_content ilike :query_like
        or applicability_note ilike :query_like
      )
    order by source_summary_count desc, updated_at desc, id desc
    limit :limit offset :offset
    """
)

COUNT_SQL = text(
    """
    select count(*) as total
    from converger_handling_advice
    where (cast(:status as varchar) is null or status = :status)
      and (cast(:primary_leaf_code as varchar) is null or primary_leaf_code = :primary_leaf_code)
      and (cast(:product_tag_code as varchar) is null or product_tag_code = :product_tag_code)
      and (cast(:request_tag_code as varchar) is null or request_tag_code = :request_tag_code)
      and (
        cast(:query as varchar) is null
        or advice_title ilike :query_like
        or advice_content ilike :query_like
        or applicability_note ilike :query_like
      )
    """
)


def _params(
    *,
    query: str | None,
    status: str | None,
    primary_leaf_code: str | None,
    product_tag_code: str | None,
    request_tag_code: str | None,
    page: int,
    page_size: int,
) -> dict[str, Any]:
    limit, offset = pagination(page, page_size)
    query_clean = _clean(query)
    return {
        "query": query_clean,
        "query_like": f"%{query_clean}%" if query_clean else None,
        "status": _clean(status),
        "primary_leaf_code": _clean(primary_leaf_code),
        "product_tag_code": _clean(product_tag_code),
        "request_tag_code": _clean(request_tag_code),
        "limit": limit,
        "offset": offset,
    }


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


@router.get("")
async def list_handling_advices(
    query: str | None = None,
    status: str | None = "active",
    primary_leaf_code: str | None = None,
    product_tag_code: str | None = None,
    request_tag_code: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    params = _params(
        query=query,
        status=status,
        primary_leaf_code=primary_leaf_code,
        product_tag_code=product_tag_code,
        request_tag_code=request_tag_code,
        page=page,
        page_size=page_size,
    )
    with get_engine().connect() as conn:
        rows = conn.execute(LIST_SQL, params).mappings().all()
        total = conn.execute(COUNT_SQL, params).scalar_one()
    return {
        "status": "success",
        "items": [jsonable_row(row) for row in rows],
        "total": total,
        "page": page,
        "page_size": params["limit"],
    }


@router.get("/{advice_id}")
async def get_handling_advice(advice_id: int) -> dict:
    with get_engine().connect() as conn:
        row = conn.execute(
            text("select * from converger_handling_advice where id = :id"),
            {"id": advice_id},
        ).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail="Handling advice not found")
    return {"status": "success", "item": jsonable_row(row)}
