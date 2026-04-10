from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from voc_agent.complaint_taxonomy_validator.nodes import analyze_ticket, load_context
from voc_agent.complaint_taxonomy_validator.state import ValidatorState

builder = StateGraph(ValidatorState)
builder.add_node('load_context', load_context)
builder.add_node('analyze_ticket', analyze_ticket)
builder.add_edge(START, 'load_context')
builder.add_edge('load_context', 'analyze_ticket')
builder.add_edge('analyze_ticket', END)

graph = builder.compile()


def run_validator(ticket_id: str) -> dict:
    state = graph.invoke({'ticket_id': ticket_id})
    return state['result']
