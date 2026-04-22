from __future__ import annotations

from typing import Any


def normalize_category_output(
    raw: dict[str, Any],
    categories: list[dict[str, Any]],
    *,
    threshold: float,
) -> dict[str, Any] | None:
    primary = raw.get('primary_category')
    if not isinstance(primary, dict):
        return None

    code = str(primary.get('code') or '').strip()
    confidence = float(primary.get('confidence', 0.0))
    if not code or confidence < threshold:
        return None

    category_by_code = {str(item['code']): item for item in categories}
    meta = category_by_code.get(code)
    if meta is None:
        return None

    return {
        'code': code,
        'full_name': primary.get('full_name') or meta.get('full_name') or meta.get('name') or code,
        'confidence': confidence,
        'reason': primary.get('reason') or raw.get('summary') or '',
    }


def normalize_tag_output(
    raw: dict[str, Any],
    tags: list[dict[str, Any]],
    *,
    threshold: float,
) -> list[dict[str, Any]]:
    tag_by_key = {(str(item['group_code']), str(item['code'])): item for item in tags}
    source_items = raw.get('candidate_tags', [])
    if not isinstance(source_items, list):
        return []

    grouped: dict[str, dict[str, Any]] = {}
    for item in source_items:
        if not isinstance(item, dict):
            continue
        group_code = str(item.get('group_code') or '').strip()
        tag_code = str(item.get('code') or '').strip()
        confidence = float(item.get('confidence', 0.0))
        if not group_code or not tag_code or confidence < threshold:
            continue
        meta = tag_by_key.get((group_code, tag_code))
        if meta is None:
            continue

        candidate = {
            'group_code': group_code,
            'code': tag_code,
            'name': item.get('name') or meta.get('name') or tag_code,
            'confidence': confidence,
            'reason': item.get('reason') or raw.get('summary') or '',
        }
        previous = grouped.get(group_code)
        if previous is None or candidate['confidence'] > previous['confidence']:
            grouped[group_code] = candidate

    return list(grouped.values())
