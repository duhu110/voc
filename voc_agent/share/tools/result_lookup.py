from __future__ import annotations

from typing import Any


def build_category_lookup(categories: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Index category metadata by category code for downstream result mapping."""
    return {str(item['code']): item for item in categories if item.get('code')}


def resolve_category_id(code: str, categories: list[dict[str, Any]]) -> int | None:
    """Resolve a category ID from a category code."""
    item = build_category_lookup(categories).get(str(code))
    if not item:
        return None
    value = item.get('id')
    return int(value) if value is not None else None


def build_tag_lookup(tags: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    """Index tag metadata by group/tag code for downstream result mapping."""
    return {
        (str(item['group_code']), str(item['code'])): item
        for item in tags
        if item.get('group_code') and item.get('code')
    }


def resolve_tag_id(group_code: str, code: str, tags: list[dict[str, Any]]) -> int | None:
    """Resolve a tag ID from group and tag codes."""
    item = build_tag_lookup(tags).get((str(group_code), str(code)))
    if not item:
        return None
    value = item.get('id')
    return int(value) if value is not None else None
