from __future__ import annotations

from typing import Any

from voc_agent.share.tools import resolve_category_id, resolve_tag_id


def _merge_primary_category(
    primary_category: dict[str, Any],
    candidate_categories: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    primary_code = str(primary_category.get('code') or '').strip()
    merged = [primary_category] if primary_code else []
    merged.extend(
        item
        for item in candidate_categories
        if str(item.get('code') or '').strip() and str(item.get('code') or '').strip() != primary_code
    )
    return merged


def _build_category_result_rows(
    ticket_id: str,
    categories_payload: list[dict[str, Any]],
    categories: list[dict[str, Any]],
    *,
    model_version: str,
    evaluation_status: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for ranking_no, item in enumerate(categories_payload, start=1):
        category_id = resolve_category_id(str(item.get('code') or ''), categories)
        if category_id is None:
            continue
        rows.append(
            {
                'ticket_id': ticket_id,
                'category_id': category_id,
                'result_source': 'ai',
                'model_version': model_version,
                'rule_version': None,
                'confidence_score': float(item.get('confidence', 0.0)),
                'ranking_no': ranking_no,
                'is_final': ranking_no == 1,
                'is_manual_confirmed': False,
                'manual_confirmed_by': None,
                'manual_confirmed_at': None,
                'matched_by': 'ai',
                'explanation': item.get('reason') or '',
                'evaluation_status': evaluation_status,
            }
        )
    return rows


def _build_tag_result_rows(
    ticket_id: str,
    tag_payload: list[dict[str, Any]],
    tags: list[dict[str, Any]],
    *,
    model_version: str,
    evaluation_status: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for ranking_no, item in enumerate(tag_payload, start=1):
        tag_id = resolve_tag_id(
            str(item.get('group_code') or ''),
            str(item.get('code') or ''),
            tags,
        )
        if tag_id is None:
            continue
        rows.append(
            {
                'ticket_id': ticket_id,
                'tag_id': tag_id,
                'result_source': 'ai',
                'model_version': model_version,
                'rule_version': None,
                'confidence_score': float(item.get('confidence', 0.0)),
                'ranking_no': ranking_no,
                'is_final': True,
                'is_manual_confirmed': False,
                'manual_confirmed_by': None,
                'manual_confirmed_at': None,
                'matched_by': 'ai',
                'explanation': item.get('reason') or '',
                'evaluation_status': evaluation_status,
            }
        )
    return rows


def _build_keyword_rows(
    ticket_id: str,
    items: list[dict[str, Any]],
    *,
    keyword_type: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in items:
        keyword = str(item.get('keyword') or '').strip()
        if not keyword:
            continue
        rows.append(
            {
                'ticket_id': ticket_id,
                'keyword': keyword,
                'keyword_type': keyword_type,
                'weight': float(item.get('confidence', 0.0)),
                'source': 'ai',
            }
        )
    return rows


def _build_match_detail_rows(
    category_rows: list[dict[str, Any]],
    tag_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in category_rows:
        rows.append(
            {
                'ticket_id': item['ticket_id'],
                'target_type': 'category',
                'target_id': item['category_id'],
                'rule_type': 'llm_reason',
                'rule_id': None,
                'matched_text': item['explanation'],
                'matched_score': item['confidence_score'],
                'matched_by': item['matched_by'],
            }
        )
    for item in tag_rows:
        rows.append(
            {
                'ticket_id': item['ticket_id'],
                'target_type': 'tag',
                'target_id': item['tag_id'],
                'rule_type': 'llm_reason',
                'rule_id': None,
                'matched_text': item['explanation'],
                'matched_score': item['confidence_score'],
                'matched_by': item['matched_by'],
            }
        )
    return rows


def build_result_rows(
    ticket_id: str,
    result: dict[str, Any],
    categories: list[dict[str, Any]],
    tags: list[dict[str, Any]],
    *,
    model_version: str,
    evaluation_status: str = 'pending',
) -> dict[str, list[dict[str, Any]]]:
    """Map validated chain output into row payloads for result/detail tables."""
    primary_category = result.get('primary_category', {}) if isinstance(result.get('primary_category'), dict) else {}
    candidate_categories = result.get('candidate_categories', [])
    merged_categories = _merge_primary_category(
        primary_category if isinstance(primary_category, dict) else {},
        candidate_categories if isinstance(candidate_categories, list) else [],
    )
    category_rows = _build_category_result_rows(
        ticket_id,
        merged_categories,
        categories,
        model_version=model_version,
        evaluation_status=evaluation_status,
    )
    tag_rows = _build_tag_result_rows(
        ticket_id,
        result.get('candidate_tags', []) if isinstance(result.get('candidate_tags'), list) else [],
        tags,
        model_version=model_version,
        evaluation_status=evaluation_status,
    )
    keyword_rows = _build_keyword_rows(
        ticket_id,
        result.get('category_keywords', []) if isinstance(result.get('category_keywords'), list) else [],
        keyword_type='category',
    )
    keyword_rows.extend(
        _build_keyword_rows(
            ticket_id,
            result.get('tag_keywords', []) if isinstance(result.get('tag_keywords'), list) else [],
            keyword_type='tag',
        )
    )
    match_detail_rows = _build_match_detail_rows(category_rows, tag_rows)
    return {
        'category_results': category_rows,
        'tag_results': tag_rows,
        'keyword_results': keyword_rows,
        'match_details': match_detail_rows,
    }
