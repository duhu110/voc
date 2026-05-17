from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from starlette.concurrency import run_in_threadpool

from backend_api.db_utils import jsonable_row, pagination
from voc_agent.advice_provider_agent import run_advice_provider
from voc_agent.core.db import get_engine

router = APIRouter(prefix="/tickets", tags=["tickets"])

LIST_SQL = text(
    """
    select
      t.ticket_id, t.accept_month, t.accept_time, t.user_city, t.line_category,
      t.biz_category, t.complaint_phenomenon, left(t.biz_content, 240) as biz_content_preview,
      t.repeat_count, t.urge_count, t.oscillation_count, t.converger_agent_status,
      r.primary_leaf_code, r.primary_leaf_name, r.product_tag_name, r.request_tag_name
    from raw_complaint_tickets t
    left join converger_agent_result r on r.ticket_id = t.ticket_id
    where (cast(:converger_agent_status as boolean) is null or t.converger_agent_status = :converger_agent_status)
      and (
        cast(:query as varchar) is null
        or t.ticket_id ilike :query_like
        or t.biz_content ilike :query_like
        or t.complaint_phenomenon ilike :query_like
      )
    order by t.created_at desc nulls last, t.ticket_id desc
    limit :limit offset :offset
    """
)

COUNT_SQL = text(
    """
    select count(*) as total
    from raw_complaint_tickets t
    where (cast(:converger_agent_status as boolean) is null or t.converger_agent_status = :converger_agent_status)
      and (
        cast(:query as varchar) is null
        or t.ticket_id ilike :query_like
        or t.biz_content ilike :query_like
        or t.complaint_phenomenon ilike :query_like
      )
    """
)


def _params(
    *,
    query: str | None,
    converger_agent_status: bool | None,
    page: int,
    page_size: int,
) -> dict[str, Any]:
    limit, offset = pagination(page, page_size)
    query_clean = query.strip() if query else None
    return {
        "query": query_clean,
        "query_like": f"%{query_clean}%" if query_clean else None,
        "converger_agent_status": converger_agent_status,
        "limit": limit,
        "offset": offset,
    }


@router.get("")
async def list_tickets(
    query: str | None = None,
    converger_agent_status: bool | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    params = _params(
        query=query,
        converger_agent_status=converger_agent_status,
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


@router.get("/{ticket_id}")
async def get_ticket(ticket_id: str) -> dict:
    with get_engine().connect() as conn:
        ticket = conn.execute(
            text("select * from raw_complaint_tickets where ticket_id = :ticket_id"),
            {"ticket_id": ticket_id},
        ).mappings().first()
        classification = conn.execute(
            text("select * from converger_agent_result where ticket_id = :ticket_id"),
            {"ticket_id": ticket_id},
        ).mappings().first()
        summary = conn.execute(
            text("select * from converger_resolution_summary_atomic where source_ticket_id = :ticket_id"),
            {"ticket_id": ticket_id},
        ).mappings().first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {
        "status": "success",
        "ticket": jsonable_row(ticket),
        "classification": jsonable_row(classification) if classification else None,
        "summary": jsonable_row(summary) if summary else None,
    }


@router.post("/{ticket_id}/advice")
async def create_ticket_advice(
    ticket_id: str,
    use_existing_classification: bool = False,
    include_processing_context: bool = False,
    advice_limit: int = 5,
    sample_limit: int = 5,
) -> dict:
    try:
        result = await run_in_threadpool(
            run_advice_provider,
            ticket_id,
            use_existing_classification=use_existing_classification,
            hide_processing_context=not include_processing_context,
            advice_limit=advice_limit,
            sample_limit=sample_limit,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "success", "result": result}
