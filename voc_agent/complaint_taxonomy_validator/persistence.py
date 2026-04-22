from __future__ import annotations

from typing import Any

from sqlalchemy import text

from voc_agent.complaint_taxonomy_validator.chain import run_validator
from voc_agent.complaint_taxonomy_validator.utils import build_result_rows
from voc_agent.core.config import get_settings
from voc_agent.core.db import get_engine
from voc_agent.share.tools import fetch_enabled_categories, fetch_enabled_tags

CATEGORY_RESULT_DELETE_SQL = text(
    """
    delete from complaint_ticket_category_result
    where ticket_id = :ticket_id and result_source = 'ai'
    """
)

TAG_RESULT_DELETE_SQL = text(
    """
    delete from complaint_ticket_tag_result
    where ticket_id = :ticket_id and result_source = 'ai'
    """
)

KEYWORD_RESULT_DELETE_SQL = text(
    """
    delete from complaint_ticket_keyword_result
    where ticket_id = :ticket_id and source = 'ai'
    """
)

MATCH_DETAIL_DELETE_SQL = text(
    """
    delete from complaint_ticket_match_detail
    where ticket_id = :ticket_id and matched_by = 'ai'
    """
)

MARK_TICKET_STATUS_SQL = text(
    """
    update raw_complaint_tickets
    set process_status = :process_status
    where ticket_id = :ticket_id
    """
)

CATEGORY_RESULT_INSERT_SQL = text(
    """
    insert into complaint_ticket_category_result (
        ticket_id,
        category_id,
        result_source,
        model_version,
        rule_version,
        confidence_score,
        ranking_no,
        is_final,
        is_manual_confirmed,
        manual_confirmed_by,
        manual_confirmed_at,
        matched_by,
        explanation,
        evaluation_status
    ) values (
        :ticket_id,
        :category_id,
        :result_source,
        :model_version,
        :rule_version,
        :confidence_score,
        :ranking_no,
        :is_final,
        :is_manual_confirmed,
        :manual_confirmed_by,
        :manual_confirmed_at,
        :matched_by,
        :explanation,
        :evaluation_status
    )
    """
)

TAG_RESULT_INSERT_SQL = text(
    """
    insert into complaint_ticket_tag_result (
        ticket_id,
        tag_id,
        result_source,
        model_version,
        rule_version,
        confidence_score,
        ranking_no,
        is_final,
        is_manual_confirmed,
        manual_confirmed_by,
        manual_confirmed_at,
        matched_by,
        explanation,
        evaluation_status
    ) values (
        :ticket_id,
        :tag_id,
        :result_source,
        :model_version,
        :rule_version,
        :confidence_score,
        :ranking_no,
        :is_final,
        :is_manual_confirmed,
        :manual_confirmed_by,
        :manual_confirmed_at,
        :matched_by,
        :explanation,
        :evaluation_status
    )
    """
)

KEYWORD_RESULT_INSERT_SQL = text(
    """
    insert into complaint_ticket_keyword_result (
        ticket_id,
        keyword,
        keyword_type,
        weight,
        source
    ) values (
        :ticket_id,
        :keyword,
        :keyword_type,
        :weight,
        :source
    )
    """
)

MATCH_DETAIL_INSERT_SQL = text(
    """
    insert into complaint_ticket_match_detail (
        ticket_id,
        target_type,
        target_id,
        rule_type,
        rule_id,
        matched_text,
        matched_score,
        matched_by
    ) values (
        :ticket_id,
        :target_type,
        :target_id,
        :rule_type,
        :rule_id,
        :matched_text,
        :matched_score,
        :matched_by
    )
    """
)


def _mark_ticket_processed(ticket_id: str, process_status: bool) -> None:
    with get_engine().begin() as conn:
        conn.execute(
            MARK_TICKET_STATUS_SQL,
            {'ticket_id': ticket_id, 'process_status': process_status},
        )


def _execute_many(conn: Any, statement: Any, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0
    conn.execute(statement, rows)
    return len(rows)


def save_validator_result(
    ticket_id: str,
    result: dict[str, Any],
    categories: list[dict[str, Any]],
    tags: list[dict[str, Any]],
    *,
    model_version: str,
) -> dict[str, int]:
    """Persist one validator result into the result/detail tables."""
    rows = build_result_rows(
        ticket_id=ticket_id,
        result=result,
        categories=categories,
        tags=tags,
        model_version=model_version,
    )

    try:
        with get_engine().begin() as conn:
            params = {'ticket_id': ticket_id}
            conn.execute(CATEGORY_RESULT_DELETE_SQL, params)
            conn.execute(TAG_RESULT_DELETE_SQL, params)
            conn.execute(KEYWORD_RESULT_DELETE_SQL, params)
            conn.execute(MATCH_DETAIL_DELETE_SQL, params)

            category_count = _execute_many(conn, CATEGORY_RESULT_INSERT_SQL, rows['category_results'])
            tag_count = _execute_many(conn, TAG_RESULT_INSERT_SQL, rows['tag_results'])
            keyword_count = _execute_many(conn, KEYWORD_RESULT_INSERT_SQL, rows['keyword_results'])
            match_detail_count = _execute_many(conn, MATCH_DETAIL_INSERT_SQL, rows['match_details'])
            conn.execute(MARK_TICKET_STATUS_SQL, {'ticket_id': ticket_id, 'process_status': True})
    except Exception:
        _mark_ticket_processed(ticket_id, False)
        raise

    return {
        'category_results': category_count,
        'tag_results': tag_count,
        'keyword_results': keyword_count,
        'match_details': match_detail_count,
    }


def run_validator_and_persist(ticket_id: str) -> dict[str, Any]:
    """Run the validator chain and persist the normalized result."""
    categories = fetch_enabled_categories()
    tags = fetch_enabled_tags()
    result = run_validator(ticket_id)
    write_summary = save_validator_result(
        ticket_id=ticket_id,
        result=result,
        categories=categories,
        tags=tags,
        model_version=get_settings().llm_model_name,
    )
    return {
        'ticket_id': ticket_id,
        'result': result,
        'write_summary': write_summary,
    }
