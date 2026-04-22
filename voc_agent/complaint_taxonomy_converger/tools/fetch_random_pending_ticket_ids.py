from __future__ import annotations

from sqlalchemy import text

from voc_agent.core.db import get_engine

RANDOM_PENDING_TICKET_QUERY = text(
    """
    select ticket_id
    from raw_complaint_tickets
    where process_status = false
    order by random()
    limit :limit
    """
)


def fetch_random_pending_ticket_ids(limit: int = 20) -> list[str]:
    with get_engine().connect() as conn:
        rows = conn.execute(RANDOM_PENDING_TICKET_QUERY, {'limit': limit}).scalars().all()
    return list(rows)
