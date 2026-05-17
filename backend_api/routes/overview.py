from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from backend_api.db_utils import jsonable_row
from voc_agent.core.db import get_engine

router = APIRouter(prefix="/overview", tags=["overview"])


@router.get("")
async def get_overview() -> dict:
    totals_sql = text(
        """
        select
          (select count(*) from raw_complaint_tickets) as raw_ticket_count,
          (select count(*) from converger_agent_result) as classified_ticket_count,
          (select count(distinct primary_leaf_code) from converger_agent_result where status = 'completed') as covered_leaf_count,
          (select count(*) from converger_resolution_summary_atomic where status = 'active') as summary_count,
          (select count(*) from converger_handling_advice where status = 'active') as active_advice_count,
          (select count(*) from expert_handling_playbook where status = 'active') as active_expert_playbook_count,
          (select count(*) from expert_handling_playbook where review_status = 'reviewed') as reviewed_expert_playbook_count,
          (select count(*) from rag_knowledge_bases where status = 'active') as active_rag_kb_count,
          (select count(*) from rag_documents where status = 'active') as active_rag_document_count
        """
    )
    trend_sql = text(
        """
        select created_at::date as processing_date, count(*) as processed_count
        from converger_agent_result
        where status = 'completed'
        group by processing_date
        order by processing_date desc
        limit 14
        """
    )
    with get_engine().connect() as conn:
        row = dict(conn.execute(totals_sql).mappings().one())
        trend_rows = conn.execute(trend_sql).mappings().all()

    raw_ticket_count = row["raw_ticket_count"] or 0
    classified_ticket_count = row["classified_ticket_count"] or 0
    row["classification_coverage_rate"] = (
        round(classified_ticket_count / raw_ticket_count, 4) if raw_ticket_count else 0
    )
    row["recent_processing_trend"] = [
        jsonable_row(trend_row) for trend_row in reversed(trend_rows)
    ]
    return {"status": "success", "data": jsonable_row(row)}


@router.get("/classification-distribution")
async def classification_distribution(limit: int = 20) -> dict:
    sql = text(
        """
        select primary_leaf_code, primary_leaf_name, count(*) as ticket_count
        from converger_agent_result
        where status = 'completed'
        group by primary_leaf_code, primary_leaf_name
        order by ticket_count desc
        limit :limit
        """
    )
    with get_engine().connect() as conn:
        rows = conn.execute(sql, {"limit": min(max(limit, 1), 100)}).mappings().all()
    return {"status": "success", "items": [jsonable_row(row) for row in rows]}
