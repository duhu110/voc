from __future__ import annotations

from sqlalchemy import text

from voc_agent.core.db import get_engine

RANDOM_TICKET_QUERY = text(
    """
    select ticket_id
    from raw_complaint_tickets
    order by random()
    limit :limit
    """
)


def fetch_random_ticket_ids(limit: int = 20) -> list[str]:
    """Fetch random ticket IDs for chain robustness validation."""
    with get_engine().connect() as conn:
        rows = conn.execute(RANDOM_TICKET_QUERY, {"limit": limit}).scalars().all()
    return list(rows)
