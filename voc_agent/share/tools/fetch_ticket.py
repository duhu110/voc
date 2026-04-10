from __future__ import annotations

from typing import Any

from sqlalchemy import text

from voc_agent.core.db import get_engine

TICKET_QUERY = text(
    """
    select *
    from raw_complaint_tickets
    where ticket_id = :ticket_id
    limit 1
    """
)


def fetch_ticket(ticket_id: str) -> dict[str, Any]:
    """Fetch one raw complaint ticket by primary key."""
    with get_engine().connect() as conn:
        row = conn.execute(TICKET_QUERY, {"ticket_id": ticket_id}).mappings().first()
    if row is None:
        raise ValueError(f"Ticket not found: {ticket_id}")
    return dict(row)
