from __future__ import annotations

from typing import Any

from sqlalchemy import text

from voc_agent.converger_agent.chain import run_converger
from voc_agent.converger_agent.utils import build_persistence_rows, load_manifest
from voc_agent.core.config import get_settings
from voc_agent.core.db import get_engine

RESULT_DELETE_SQL = text(
    """
    delete from converger_agent_result
    where ticket_id = :ticket_id
    """
)

RESOLUTION_SUMMARY_DELETE_SQL = text(
    """
    delete from converger_resolution_summary_atomic
    where source_ticket_id = :ticket_id
    """
)

MARK_TICKET_STATUS_SQL = text(
    """
    update raw_complaint_tickets
    set converger_agent_status = :converger_agent_status
    where ticket_id = :ticket_id
    """
)

RESULT_INSERT_SQL = text(
    """
    insert into converger_agent_result (
        ticket_id,
        primary_level1_code,
        primary_level1_name,
        primary_level2_code,
        primary_level2_name,
        primary_leaf_code,
        primary_leaf_name,
        request_tag_code,
        request_tag_name,
        emotion_tag_code,
        emotion_tag_name,
        risk_tag_code,
        risk_tag_name,
        product_tag_code,
        product_tag_name,
        line_category,
        model_name,
        taxonomy_version,
        agent_version,
        status
    ) values (
        :ticket_id,
        :primary_level1_code,
        :primary_level1_name,
        :primary_level2_code,
        :primary_level2_name,
        :primary_leaf_code,
        :primary_leaf_name,
        :request_tag_code,
        :request_tag_name,
        :emotion_tag_code,
        :emotion_tag_name,
        :risk_tag_code,
        :risk_tag_name,
        :product_tag_code,
        :product_tag_name,
        :line_category,
        :model_name,
        :taxonomy_version,
        :agent_version,
        :status
    )
    """
)

RESOLUTION_SUMMARY_INSERT_SQL = text(
    """
    insert into converger_resolution_summary_atomic (
        source_ticket_id,
        primary_leaf_code,
        primary_leaf_name,
        product_tag_code,
        product_tag_name,
        request_tag_code,
        request_tag_name,
        risk_tag_code,
        risk_tag_name,
        emotion_tag_code,
        emotion_tag_name,
        line_category,
        resolution_summary,
        model_name,
        taxonomy_version,
        agent_version,
        status
    ) values (
        :source_ticket_id,
        :primary_leaf_code,
        :primary_leaf_name,
        :product_tag_code,
        :product_tag_name,
        :request_tag_code,
        :request_tag_name,
        :risk_tag_code,
        :risk_tag_name,
        :emotion_tag_code,
        :emotion_tag_name,
        :line_category,
        :resolution_summary,
        :model_name,
        :taxonomy_version,
        :agent_version,
        :status
    )
    """
)


def _mark_ticket_processed(ticket_id: str, converger_agent_status: bool) -> None:
    with get_engine().begin() as conn:
        conn.execute(
            MARK_TICKET_STATUS_SQL,
            {
                "ticket_id": ticket_id,
                "converger_agent_status": converger_agent_status,
            },
        )


def _execute_one(conn: Any, statement: Any, row: dict[str, Any] | None) -> int:
    if not row:
        return 0
    conn.execute(statement, row)
    return 1


def save_converger_result(
    *,
    ticket_id: str,
    result: dict[str, Any],
    model_name: str,
    taxonomy_version: str,
    agent_version: str,
) -> dict[str, int]:
    rows = build_persistence_rows(
        result=result,
        model_name=model_name,
        taxonomy_version=taxonomy_version,
        agent_version=agent_version,
    )

    try:
        with get_engine().begin() as conn:
            conn.execute(RESULT_DELETE_SQL, {"ticket_id": ticket_id})
            conn.execute(RESOLUTION_SUMMARY_DELETE_SQL, {"ticket_id": ticket_id})

            result_count = _execute_one(conn, RESULT_INSERT_SQL, rows["result_row"])
            resolution_summary_count = _execute_one(
                conn,
                RESOLUTION_SUMMARY_INSERT_SQL,
                rows["resolution_summary_row"],
            )
            conn.execute(
                MARK_TICKET_STATUS_SQL,
                {
                    "ticket_id": ticket_id,
                    "converger_agent_status": True,
                },
            )
    except Exception:
        _mark_ticket_processed(ticket_id, False)
        raise

    return {
        "result_rows": result_count,
        "resolution_summary_rows": resolution_summary_count,
    }


def run_converger_and_persist(ticket_id: str) -> dict[str, Any]:
    manifest = load_manifest()
    settings = get_settings()
    result = run_converger(ticket_id)
    write_summary = save_converger_result(
        ticket_id=ticket_id,
        result=result,
        model_name=settings.llm_model_name,
        taxonomy_version=str(manifest["version"]),
        agent_version="v1",
    )
    return {
        "ticket_id": ticket_id,
        "result": result,
        "write_summary": write_summary,
    }
