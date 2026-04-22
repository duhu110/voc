from __future__ import annotations

from typing import Any

from sqlalchemy import text

from voc_agent.core.db import get_engine

TAG_QUERY = text(
    """
    select
        t.id,
        g.code as group_code,
        g.name as group_name,
        t.code,
        t.name,
        t.description
    from complaint_tag t
    join complaint_tag_group g on g.id = t.group_id
    where t.is_enabled = true and g.is_enabled = true
    order by g.sort_order, g.id, t.sort_order, t.id
    """
)


def fetch_enabled_tags() -> list[dict[str, Any]]:
    """Fetch all enabled tags grouped by tag group metadata."""
    with get_engine().connect() as conn:
        rows = conn.execute(TAG_QUERY).mappings().all()
    return [dict(row) for row in rows]
