from __future__ import annotations

from sqlalchemy import text

from voc_agent.core.db import get_engine

PENDING_TICKET_QUERY = text(
    """
    select ticket_id
    from raw_complaint_tickets
    where process_status = false
    order by created_at desc nulls last, ticket_id desc
    limit :limit
    """
)


def fetch_pending_ticket_ids(limit: int = 20) -> list[str]:
    """Fetch unprocessed ticket IDs for batch validation and persistence."""
    with get_engine().connect() as conn:
        rows = conn.execute(PENDING_TICKET_QUERY, {"limit": limit}).scalars().all()
    return list(rows)
