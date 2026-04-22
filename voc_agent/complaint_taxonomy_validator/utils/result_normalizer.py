from __future__ import annotations

from typing import Any

from voc_agent.share.utils import parse_bracket_code


def _normalize_category_candidate(
    item: dict[str, Any],
    category_by_code: dict[str, dict[str, Any]],
    *,
    default_confidence: float,
    default_reason: str,
) -> dict[str, Any] | None:
    code = str(item.get('code') or item.get('category_code') or '').strip()
    if not code:
        return None
    meta = category_by_code.get(code, {})
    return {
        'code': code,
        'full_name': item.get('full_name') or meta.get('full_name') or meta.get('name') or code,
        'confidence': float(item.get('confidence', default_confidence)),
        'reason': item.get('reason') or default_reason,
    }


def coerce_keyword_items(items: list[Any]) -> list[dict[str, Any]]:
    """Normalize loose keyword output into the validator schema."""
    results: list[dict[str, Any]] = []
    for item in items:
        if isinstance(item, str):
            results.append(
                {
                    'keyword': item,
                    'reason': '模型识别为与当前判断有关的关键词',
                    'confidence': 0.7,
                }
            )
            continue
        if isinstance(item, dict):
            results.append(
                {
                    'keyword': item.get('keyword') or item.get('text') or item.get('value') or '',
                    'reason': item.get('reason') or '模型识别为与当前判断有关的关键词',
                    'confidence': float(item.get('confidence', 0.7)),
                }
            )
    return [item for item in results if item['keyword']]


def normalize_result(raw: dict[str, Any], categories: list[dict[str, Any]], tags: list[dict[str, Any]]) -> dict[str, Any]:
    """Map provider-specific JSON output to the validator output schema."""
    category_by_code = {str(item['code']): item for item in categories}
    tag_by_key = {(str(item['group_code']), str(item['code'])): item for item in tags}

    classification = raw.get('classification', {}) if isinstance(raw.get('classification'), dict) else {}
    reason = classification.get('reason') or raw.get('summary') or '模型已给出分类判断，但未提供完整摘要。'

    category_candidates: list[dict[str, Any]] = []
    if isinstance(raw.get('candidate_categories'), list):
        for item in raw['candidate_categories']:
            if not isinstance(item, dict):
                continue
            normalized_item = _normalize_category_candidate(
                item,
                category_by_code,
                default_confidence=0.7,
                default_reason=reason,
            )
            if normalized_item:
                category_candidates.append(normalized_item)

    normalized_primary = None
    if isinstance(raw.get('primary_category'), dict):
        normalized_primary = _normalize_category_candidate(
            raw['primary_category'],
            category_by_code,
            default_confidence=0.8,
            default_reason=reason,
        )

    if not category_candidates and normalized_primary:
        category_candidates.append(normalized_primary)

    if not category_candidates:
        for key, confidence in [
            ('secondary_category', 0.9),
            ('primary_category', 0.8),
            ('tertiary_category', 0.7),
            ('quaternary_category', 0.6),
        ]:
            value = classification.get(key)
            if not value:
                continue
            code = parse_bracket_code(str(value))[-1]
            meta = category_by_code.get(code, {})
            category_candidates.append(
                {
                    'code': code,
                    'full_name': meta.get('full_name') or meta.get('name') or code,
                    'confidence': confidence,
                    'reason': reason,
                }
            )

    tag_candidates: list[dict[str, Any]] = []
    source_tags = raw.get('tags', []) if isinstance(raw.get('tags'), list) else raw.get('candidate_tags', [])
    for item in source_tags:
        if isinstance(item, dict):
            raw_group_code = str(item.get('group_code') or '').strip()
            raw_tag_code = str(item.get('code') or '').strip()
            parsed_parts = parse_bracket_code(raw_tag_code)
            group_code = raw_group_code
            tag_code = raw_tag_code
            if len(parsed_parts) >= 2:
                group_code = group_code or parsed_parts[0]
                tag_code = parsed_parts[1]
            meta = tag_by_key.get((group_code, tag_code), {})
            tag_candidates.append(
                {
                    'group_code': group_code,
                    'code': tag_code,
                    'name': item.get('name') or meta.get('name') or tag_code,
                    'confidence': float(item.get('confidence', 0.8)),
                    'reason': item.get('reason') or reason,
                }
            )
            continue
        if not isinstance(item, str):
            continue
        parts = parse_bracket_code(item)
        if len(parts) < 2:
            continue
        group_code, tag_code = parts[0], parts[1]
        meta = tag_by_key.get((group_code, tag_code), {})
        tag_candidates.append(
            {
                'group_code': group_code,
                'code': tag_code,
                'name': meta.get('name') or tag_code,
                'confidence': 0.8,
                'reason': reason,
            }
        )

    primary_category = normalized_primary or (category_candidates[0] if category_candidates else {
        'code': 'UNKNOWN',
        'full_name': 'UNKNOWN',
        'confidence': 0.0,
        'reason': '模型未返回可识别的分类结果。',
    })
    primary_code = str(primary_category.get('code') or '').strip()
    merged_category_candidates = [primary_category]
    merged_category_candidates.extend(
        item
        for item in category_candidates
        if str(item.get('code') or '').strip() and str(item.get('code') or '').strip() != primary_code
    )

    return {
        'summary': raw.get('summary') or reason,
        'primary_category': primary_category,
        'candidate_categories': merged_category_candidates,
        'candidate_tags': tag_candidates,
        'category_keywords': coerce_keyword_items(raw.get('category_keywords', [])),
        'tag_keywords': coerce_keyword_items(raw.get('tag_keywords', [])),
        'risks': raw.get('risks', []),
    }
