from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from voc_agent.converger_agent.nodes import (
    analyze_controlled_tags,
    analyze_primary_category,
    finalize_result,
    load_context,
    summarize_resolution,
)
from voc_agent.converger_agent.state import ConvergerState


def _route_after_primary_category(state: ConvergerState) -> str:
    if state.get("status") == "category_selected":
        return "analyze_controlled_tags"
    return "finalize_result"


def build_graph():
    builder = StateGraph(ConvergerState)
    builder.add_node("load_context", load_context)
    builder.add_node("analyze_primary_category", analyze_primary_category)
    builder.add_node("analyze_controlled_tags", analyze_controlled_tags)
    builder.add_node("summarize_resolution", summarize_resolution)
    builder.add_node("finalize_result", finalize_result)

    builder.add_edge(START, "load_context")
    builder.add_edge("load_context", "analyze_primary_category")
    builder.add_conditional_edges(
        "analyze_primary_category",
        _route_after_primary_category,
        {
            "analyze_controlled_tags": "analyze_controlled_tags",
            "finalize_result": "finalize_result",
        },
    )
    builder.add_edge("analyze_controlled_tags", "summarize_resolution")
    builder.add_edge("summarize_resolution", "finalize_result")
    builder.add_edge("finalize_result", END)
    return builder.compile()


graph = build_graph()


def run_converger(ticket_id: str) -> dict:
    state = graph.invoke({"ticket_id": ticket_id})
    return state["result"]
