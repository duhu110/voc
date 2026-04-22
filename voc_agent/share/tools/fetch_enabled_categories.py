from __future__ import annotations

from typing import Any

from sqlalchemy import text

from voc_agent.core.db import get_engine

CATEGORY_QUERY = text(
    """
    select
        id,
        code,
        name,
        level,
        full_name,
        description,
        keywords
    from complaint_category
    where is_enabled = true
    order by level, sort_order, id
    """
)


def fetch_enabled_categories() -> list[dict[str, Any]]:
    """Fetch all enabled complaint categories for taxonomy selection."""
    with get_engine().connect() as conn:
        rows = conn.execute(CATEGORY_QUERY).mappings().all()
    return [dict(row) for row in rows]
