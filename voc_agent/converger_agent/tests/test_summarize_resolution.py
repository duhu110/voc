from __future__ import annotations

from importlib import import_module

summarize_resolution_module = import_module("voc_agent.converger_agent.nodes.summarize_resolution")


class _FakeResponse:
    def __init__(self, content: str) -> None:
        self.choices = [type("Choice", (), {"message": type("Message", (), {"content": content})()})()]


class _FakeCompletions:
    def __init__(self, content: str) -> None:
        self._content = content

    def create(self, **_: object) -> _FakeResponse:
        return _FakeResponse(self._content)


class _FakeClient:
    def __init__(self, content: str) -> None:
        self.chat = type("Chat", (), {"completions": _FakeCompletions(content)})()


def test_summarize_resolution_returns_summary_when_present(monkeypatch) -> None:
    fake_content = """
{
  "resolution_summary": "先核实礼包合约告知口径，再按取消条件与用户协商处理。"
}
"""
    monkeypatch.setattr(summarize_resolution_module, "_create_openai_client", lambda: _FakeClient(fake_content))
    monkeypatch.setattr(
        summarize_resolution_module,
        "get_settings",
        lambda: type(
            "Settings",
            (),
            {
                "llm_model_name": "Qwen3-Max",
                "llm_temperature": 0,
            },
        )(),
    )

    result = summarize_resolution_module.summarize_resolution(
        {
            "ticket": {
                "ticket_id": "T-1",
                "return_reason": "留单原因",
                "prov_process_desc": "已解释合约规则。",
            },
            "primary_category": {
                "leaf_code": "MISLEADING_EXPLANATION",
                "leaf_name": "宣传/解释不清或误导",
            },
            "request_tag": {"code": "CANCEL", "name": "取消业务", "reason": "要求取消"},
            "product_tag": {"code": "VALUE_ADDED", "name": "增值业务", "reason": "礼包业务"},
        }
    )

    assert result["status"] == "resolution_summarized"
    assert result["resolution_summary"] == "先核实礼包合约告知口径，再按取消条件与用户协商处理。"


def test_summarize_resolution_skips_when_no_processing_fields() -> None:
    result = summarize_resolution_module.summarize_resolution(
        {
            "ticket": {
                "ticket_id": "T-2",
                "biz_content": "只有投诉内容，没有处理过程。",
            }
        }
    )

    assert result["status"] == "resolution_unavailable"
    assert result["resolution_summary"] is None
