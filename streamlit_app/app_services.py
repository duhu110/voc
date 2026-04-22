from __future__ import annotations

import json
import time
import traceback
from collections import Counter
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy import text
from sqlalchemy.engine import Engine

from voc_agent.complaint_taxonomy_validator.batch_persistence import OUTPUT_DIR as BATCH_OUTPUT_DIR
from voc_agent.complaint_taxonomy_validator.nodes import load_context
from voc_agent.complaint_taxonomy_validator.persistence import save_validator_result
from voc_agent.complaint_taxonomy_validator.prompts import SYSTEM_PROMPT, build_user_prompt
from voc_agent.complaint_taxonomy_validator.persistence import run_validator_and_persist
from voc_agent.complaint_taxonomy_validator.state import ValidatorOutput
from voc_agent.complaint_taxonomy_validator.stats_aggregation import refresh_statistics
from voc_agent.complaint_taxonomy_validator.utils import normalize_result
from voc_agent.complaint_taxonomy_validator.tools import fetch_pending_ticket_ids
from voc_agent.core.config import get_settings
from voc_agent.core.db import get_engine
from voc_agent.core.llm import get_chat_model
from voc_agent.share.utils import parse_json_payload_once

DASHBOARD_QUERIES = {
    'pending_tickets': "select count(*) from raw_complaint_tickets where process_status = false",
    'processed_tickets': "select count(*) from raw_complaint_tickets where process_status = true",
    'category_results': "select count(*) from complaint_ticket_category_result where result_source = 'ai'",
    'tag_results': "select count(*) from complaint_ticket_tag_result where result_source = 'ai'",
    'keyword_results': "select count(*) from complaint_ticket_keyword_result where source = 'ai'",
    'match_details': "select count(*) from complaint_ticket_match_detail where matched_by = 'ai'",
    'category_stats': "select count(*) from complaint_category_stats",
    'tag_stats': "select count(*) from complaint_tag_stats",
}

RANDOM_PENDING_TICKET_QUERY = text(
    """
    select ticket_id
    from raw_complaint_tickets
    where process_status = false
    order by random()
    limit 1
    """
)

TABLE_QUERIES = {
    'pending_tickets': """
        select ticket_id, process_status
        from raw_complaint_tickets
        where process_status = false
        order by ticket_id desc
        limit :limit
    """,
    'category_results': """
        select ticket_id, category_id, confidence_score, ranking_no, is_final, created_at
        from complaint_ticket_category_result
        where result_source = 'ai'
        order by created_at desc, id desc
        limit :limit
    """,
    'tag_results': """
        select ticket_id, tag_id, confidence_score, ranking_no, is_final, created_at
        from complaint_ticket_tag_result
        where result_source = 'ai'
        order by created_at desc, id desc
        limit :limit
    """,
    'keyword_results': """
        select ticket_id, keyword, keyword_type, weight, source, created_at
        from complaint_ticket_keyword_result
        where source = 'ai'
        order by created_at desc, id desc
        limit :limit
    """,
    'match_details': """
        select ticket_id, target_type, target_id, matched_text, matched_score, matched_by, created_at
        from complaint_ticket_match_detail
        where matched_by = 'ai'
        order by created_at desc, id desc
        limit :limit
    """,
    'category_stats': """
        select category_id, stat_date, total_predicted_count, total_final_count, avg_confidence_score
        from complaint_category_stats
        order by stat_date desc, total_predicted_count desc, category_id asc
        limit :limit
    """,
    'tag_stats': """
        select tag_id, stat_date, total_predicted_count, total_final_count, avg_confidence_score
        from complaint_tag_stats
        order by stat_date desc, total_predicted_count desc, tag_id asc
        limit :limit
    """,
    'category_tag_relations': """
        select category_id, tag_id, sample_count, cooccurrence_count, cooccurrence_rate, relation_strength
        from complaint_category_tag_stat_relation
        order by cooccurrence_count desc, category_id asc, tag_id asc
        limit :limit
    """,
    'category_keyword_stats': """
        select category_id, keyword, sample_count, hit_count, confidence_score
        from complaint_category_keyword_stat
        order by hit_count desc, category_id asc, keyword asc
        limit :limit
    """,
    'tag_keyword_stats': """
        select tag_id, keyword, sample_count, hit_count, confidence_score
        from complaint_tag_keyword_stat
        order by hit_count desc, tag_id asc, keyword asc
        limit :limit
    """,
}

TICKET_RESULT_QUERIES = {
    'category_results': """
        select ticket_id, category_id, confidence_score, ranking_no, is_final, created_at
        from complaint_ticket_category_result
        where ticket_id = :ticket_id and result_source = 'ai'
        order by ranking_no asc, id asc
    """,
    'tag_results': """
        select ticket_id, tag_id, confidence_score, ranking_no, is_final, created_at
        from complaint_ticket_tag_result
        where ticket_id = :ticket_id and result_source = 'ai'
        order by ranking_no asc, id asc
    """,
    'keyword_results': """
        select ticket_id, keyword, keyword_type, weight, source, created_at
        from complaint_ticket_keyword_result
        where ticket_id = :ticket_id and source = 'ai'
        order by id asc
    """,
    'match_details': """
        select ticket_id, target_type, target_id, matched_text, matched_score, matched_by, created_at
        from complaint_ticket_match_detail
        where ticket_id = :ticket_id and matched_by = 'ai'
        order by id asc
    """,
}


def _resolve_engine(engine: Engine | None = None) -> Engine:
    return engine or get_engine()


def list_batch_summaries(output_dir: Path = BATCH_OUTPUT_DIR) -> list[Path]:
    if not output_dir.exists():
        return []
    return sorted(output_dir.glob('summary__*.json'), reverse=True)


def load_summary_artifact(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _json_default(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat(timespec='seconds')
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return str(value)


def dumps_for_ui(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default)


def build_batch_result_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for result in summary.get('results', []):
        write_summary = result.get('write_summary') or {}
        rows.append(
            {
                'ticket_id': result.get('ticket_id'),
                'status': result.get('status'),
                'duration_ms': result.get('duration_ms'),
                'category_results': write_summary.get('category_results', 0),
                'tag_results': write_summary.get('tag_results', 0),
                'keyword_results': write_summary.get('keyword_results', 0),
                'match_details': write_summary.get('match_details', 0),
                'error_type': result.get('error_type'),
                'error_message': result.get('error_message'),
            }
        )
    return rows


def run_batch_job(sample_size: int) -> dict[str, Any]:
    settings = get_settings()
    ticket_ids = fetch_pending_ticket_ids(limit=sample_size)
    if len(ticket_ids) != sample_size:
        raise RuntimeError(f'Expected {sample_size} pending ticket IDs, got {len(ticket_ids)}')

    failures_by_stage: Counter[str] = Counter()
    summary: dict[str, Any] = {
        'timestamp': datetime.now().isoformat(timespec='seconds'),
        'sample_size': sample_size,
        'model_name': settings.llm_model_name,
        'ticket_ids': ticket_ids,
        'success_count': 0,
        'failure_count': 0,
        'success_rate': 0.0,
        'failures_by_stage': {},
        'results': [],
    }

    for ticket_id in ticket_ids:
        started_at = time.perf_counter()
        try:
            persisted = run_validator_and_persist(ticket_id)
            payload = {
                'ticket_id': ticket_id,
                'status': 'success',
                'stage': 'persistence',
                'duration_ms': int((time.perf_counter() - started_at) * 1000),
                'timestamp': datetime.now().isoformat(timespec='seconds'),
                'model_name': settings.llm_model_name,
                'write_summary': persisted['write_summary'],
                'result': persisted.get('result'),
            }
            summary['success_count'] += 1
        except Exception as exc:  # noqa: BLE001
            failures_by_stage['persistence'] += 1
            payload = {
                'ticket_id': ticket_id,
                'status': 'failed',
                'stage': 'persistence',
                'duration_ms': int((time.perf_counter() - started_at) * 1000),
                'timestamp': datetime.now().isoformat(timespec='seconds'),
                'model_name': settings.llm_model_name,
                'error_type': exc.__class__.__name__,
                'error_message': str(exc),
                'traceback': ''.join(traceback.format_exception(exc)),
            }
            summary['failure_count'] += 1

        summary['results'].append(payload)

    summary['success_rate'] = summary['success_count'] / sample_size if sample_size else 0.0
    summary['failures_by_stage'] = dict(failures_by_stage)
    return summary


def run_statistics_refresh(stat_date: str | None = None) -> dict[str, Any]:
    return refresh_statistics(stat_date=stat_date)


def fetch_random_pending_ticket_id(*, engine: Engine | None = None) -> str:
    resolved_engine = _resolve_engine(engine)
    with resolved_engine.connect() as conn:
        ticket_id = conn.execute(RANDOM_PENDING_TICKET_QUERY).scalar()
    if not ticket_id:
        raise RuntimeError('No unprocessed ticket found in raw_complaint_tickets')
    return str(ticket_id)


def fetch_ticket_result_rows(ticket_id: str, *, engine: Engine | None = None) -> dict[str, list[dict[str, Any]]]:
    resolved_engine = _resolve_engine(engine)
    result: dict[str, list[dict[str, Any]]] = {}
    with resolved_engine.connect() as conn:
        for key, sql in TICKET_RESULT_QUERIES.items():
            rows = conn.execute(text(sql), {'ticket_id': ticket_id}).mappings().all()
            result[key] = [dict(row) for row in rows]
    return result


def stream_single_ticket_job(ticket_id: str | None):
    resolved_ticket_id = ticket_id.strip() if ticket_id and ticket_id.strip() else fetch_random_pending_ticket_id()
    settings = get_settings()
    started_at = datetime.now().isoformat(timespec='seconds')
    yield {
        'stage': 'start',
        'ticket_id': resolved_ticket_id,
        'timestamp': started_at,
        'message': f'开始执行工单 {resolved_ticket_id}',
        'model_name': settings.llm_model_name,
    }

    context = load_context({'ticket_id': resolved_ticket_id})
    yield {
        'stage': 'context_loaded',
        'ticket_id': resolved_ticket_id,
        'ticket': context['ticket'],
        'categories': context['categories'],
        'tags': context['tags'],
        'category_count': len(context['categories']),
        'tag_count': len(context['tags']),
        'message': '工单、分类、标签上下文加载完成',
    }

    prompt = build_user_prompt(
        ticket=context['ticket'],
        categories=context['categories'],
        tags=context['tags'],
    )
    yield {
        'stage': 'prompt_built',
        'ticket_id': resolved_ticket_id,
        'prompt': prompt,
        'prompt_length': len(prompt),
        'message': 'Prompt 构造完成',
    }

    llm = get_chat_model()
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt + '\n\n请只返回纯 JSON，不要使用 Markdown 代码块。'),
    ])
    raw_text = response.text if hasattr(response, 'text') else str(response.content)
    yield {
        'stage': 'llm_response',
        'ticket_id': resolved_ticket_id,
        'raw_text': raw_text,
        'message': '模型返回完成',
    }

    raw_data = parse_json_payload_once(raw_text)
    normalized = normalize_result(raw_data, context['categories'], context['tags'])
    parsed = ValidatorOutput.model_validate(normalized)
    result = parsed.model_dump(mode='json')
    yield {
        'stage': 'result_parsed',
        'ticket_id': resolved_ticket_id,
        'raw_data': raw_data,
        'result': result,
        'message': '返回结果已标准化并通过结构校验',
    }

    write_summary = save_validator_result(
        ticket_id=resolved_ticket_id,
        result=result,
        categories=context['categories'],
        tags=context['tags'],
        model_version=settings.llm_model_name,
    )
    yield {
        'stage': 'persisted',
        'ticket_id': resolved_ticket_id,
        'result': result,
        'write_summary': write_summary,
        'message': '结果已落库',
    }

    database_rows = fetch_ticket_result_rows(resolved_ticket_id)
    yield {
        'stage': 'database_rows_loaded',
        'ticket_id': resolved_ticket_id,
        'database_rows': database_rows,
        'message': '已回查数据库中的真实结果行',
    }


def fetch_dashboard_snapshot(*, engine: Engine | None = None) -> dict[str, int]:
    resolved_engine = _resolve_engine(engine)
    snapshot: dict[str, int] = {}
    with resolved_engine.connect() as conn:
        for key, sql in DASHBOARD_QUERIES.items():
            snapshot[key] = int(conn.execute(text(sql)).scalar() or 0)
    return snapshot


def fetch_table_rows(table_key: str, *, limit: int = 50, engine: Engine | None = None) -> list[dict[str, Any]]:
    sql = TABLE_QUERIES.get(table_key)
    if sql is None:
        raise ValueError(f'Unsupported table key: {table_key}')

    resolved_engine = _resolve_engine(engine)
    with resolved_engine.connect() as conn:
        rows = conn.execute(text(sql), {'limit': limit}).mappings().all()
    return [dict(row) for row in rows]
