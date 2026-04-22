from __future__ import annotations

from importlib import import_module

chain_module = import_module("voc_agent.converger_agent.chain")


def test_build_graph_routes_to_tags_and_finalize(monkeypatch) -> None:
    call_order: list[str] = []

    def fake_load_context(state):
        call_order.append("load_context")
        return {"ticket": {"ticket_id": state["ticket_id"]}, "runtime_data": {}}

    def fake_analyze_primary_category(state):
        call_order.append("analyze_primary_category")
        return {
            "status": "category_selected",
            "category_summary": "ok",
            "primary_category": {
                "level1_code": "A",
                "level1_name": "A",
                "level2_code": "B",
                "level2_name": "B",
                "leaf_code": "C",
                "leaf_name": "C",
                "reason": "x",
            },
        }

    def fake_analyze_controlled_tags(state):
        call_order.append("analyze_controlled_tags")
        return {
            "status": "tags_selected",
            "request_tag": {"code": "R", "name": "R", "reason": "r"},
            "emotion_tag": {"code": "E", "name": "E", "reason": "e"},
            "risk_tag": {"code": "K", "name": "K", "reason": "k"},
            "product_tag": {"code": "P", "name": "P", "reason": "p"},
            "line_category": {"value": "L", "reason": "direct"},
        }

    def fake_summarize_resolution(state):
        call_order.append("summarize_resolution")
        return {
            "status": "resolution_summarized",
            "resolution_summary": "总结",
        }

    def fake_finalize_result(state):
        call_order.append("finalize_result")
        return {"result": {"ticket_id": state["ticket_id"], "status": "completed"}}

    monkeypatch.setattr(chain_module, "load_context", fake_load_context)
    monkeypatch.setattr(chain_module, "analyze_primary_category", fake_analyze_primary_category)
    monkeypatch.setattr(chain_module, "analyze_controlled_tags", fake_analyze_controlled_tags)
    monkeypatch.setattr(chain_module, "summarize_resolution", fake_summarize_resolution)
    monkeypatch.setattr(chain_module, "finalize_result", fake_finalize_result)

    graph = chain_module.build_graph()
    result = graph.invoke({"ticket_id": "T-1"})

    assert call_order == [
        "load_context",
        "analyze_primary_category",
        "analyze_controlled_tags",
        "summarize_resolution",
        "finalize_result",
    ]
    assert result["result"]["status"] == "completed"
