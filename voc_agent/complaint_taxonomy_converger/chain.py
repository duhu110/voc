from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from voc_agent.complaint_taxonomy_converger.nodes import analyze_category, analyze_tags, finalize_result, load_context
from voc_agent.complaint_taxonomy_converger.state import ConvergerState


def route_after_category(state: ConvergerState) -> str:
    return 'analyze_tags' if state.get('selected_category') else 'finalize_result'


builder = StateGraph(ConvergerState)
builder.add_node('load_context', load_context)
builder.add_node('analyze_category', analyze_category)
builder.add_node('analyze_tags', analyze_tags)
builder.add_node('finalize_result', finalize_result)
builder.add_edge(START, 'load_context')
builder.add_edge('load_context', 'analyze_category')
builder.add_conditional_edges(
    'analyze_category',
    route_after_category,
    {
        'analyze_tags': 'analyze_tags',
        'finalize_result': 'finalize_result',
    },
)
builder.add_edge('analyze_tags', 'finalize_result')
builder.add_edge('finalize_result', END)

graph = builder.compile()


def run_converger(ticket_id: str) -> dict:
    state = graph.invoke({'ticket_id': ticket_id})
    return state['result']
