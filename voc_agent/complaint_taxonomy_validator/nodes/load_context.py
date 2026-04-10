from __future__ import annotations

from voc_agent.complaint_taxonomy_validator.state import ValidatorState
from voc_agent.share.tools import fetch_enabled_categories, fetch_enabled_tags, fetch_ticket


def load_context(state: ValidatorState) -> ValidatorState:
    """Load ticket, category, and tag context before LLM analysis."""
    ticket_id = state['ticket_id']
    return {
        'ticket_id': ticket_id,
        'ticket': fetch_ticket(ticket_id),
        'categories': fetch_enabled_categories(),
        'tags': fetch_enabled_tags(),
    }
