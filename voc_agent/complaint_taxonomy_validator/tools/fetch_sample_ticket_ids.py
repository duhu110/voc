from __future__ import annotations

from sqlalchemy import text

from voc_agent.core.db import get_engine

SAMPLE_TICKET_QUERY = text(
    """
    select ticket_id
    from raw_complaint_tickets
    order by created_at desc nulls last, ticket_id desc
    limit :limit
    """
)


def fetch_sample_ticket_ids(limit: int = 5) -> list[str]:
    """Fetch recent ticket IDs for validator debugging and smoke tests."""
    with get_engine().connect() as conn:
        rows = conn.execute(SAMPLE_TICKET_QUERY, {"limit": limit}).scalars().all()
    return list(rows)
