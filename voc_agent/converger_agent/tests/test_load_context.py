from __future__ import annotations

from importlib import import_module

load_context_module = import_module("voc_agent.converger_agent.nodes.load_context")


def test_load_context_fetches_ticket_and_runtime_data(monkeypatch) -> None:
    fake_ticket = {"ticket_id": "T-1", "biz_content": "用户不认可收费。"}
    fake_runtime_data = {"category": {"leaves": {}}, "request_tags": {}, "emotion_tags": {}, "risk_tags": {}, "product_tags": {}}

    monkeypatch.setattr(load_context_module, "fetch_ticket", lambda ticket_id: {**fake_ticket, "ticket_id": ticket_id})
    monkeypatch.setattr(load_context_module, "load_runtime_data", lambda: fake_runtime_data)

    result = load_context_module.load_context({"ticket_id": "T-1"})

    assert result["ticket"]["ticket_id"] == "T-1"
    assert result["runtime_data"] is fake_runtime_data

