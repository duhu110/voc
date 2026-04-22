from __future__ import annotations

from voc_agent.converger_agent.state import ConvergerState
from voc_agent.converger_agent.utils import load_runtime_data
from voc_agent.share.tools import fetch_ticket


def load_context(state: ConvergerState) -> ConvergerState:
    ticket_id = state["ticket_id"]
    ticket = fetch_ticket(ticket_id)
    runtime_data = load_runtime_data()
    return {
        "ticket": ticket,
        "runtime_data": runtime_data,
    }
