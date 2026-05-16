from __future__ import annotations

from fastapi.testclient import TestClient

from backend_api.main import create_app
from backend_api.routes import advice


def test_advice_route_calls_payload_provider(monkeypatch) -> None:
    captured = {}

    def fake_provider(ticket, **kwargs):
        captured["ticket"] = ticket
        captured["kwargs"] = kwargs
        return {"ticket_id": ticket["ticket_id"], "final_action_plan": {"steps": []}}

    monkeypatch.setattr(advice, "run_advice_provider_for_ticket_payload", fake_provider)

    client = TestClient(create_app())
    response = client.post(
        "/agent/advice",
        json={
            "ticket_payload": {
                "ticket_id": "tmp-1",
                "biz_content": "用户投诉费用异常，要求核实处理。",
            },
            "advice_limit": 3,
            "sample_limit": 2,
        },
    )

    assert response.status_code == 200
    assert response.json()["result"]["ticket_id"] == "tmp-1"
    assert captured["kwargs"]["advice_limit"] == 3
    assert captured["kwargs"]["sample_limit"] == 2


def test_advice_route_requires_single_ticket_source() -> None:
    client = TestClient(create_app())
    response = client.post("/agent/advice", json={})

    assert response.status_code == 422

