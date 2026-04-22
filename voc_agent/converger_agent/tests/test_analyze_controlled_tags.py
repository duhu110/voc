from __future__ import annotations

from importlib import import_module

analyze_controlled_tags_module = import_module("voc_agent.converger_agent.nodes.analyze_controlled_tags")


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


def test_analyze_controlled_tags_returns_mapped_tag_details(monkeypatch) -> None:
    runtime_data = {
        "request_tags": {
            "items": [{"code": "EXPLAIN", "name": "解释说明", "desc": "需要解释。"}],
        },
        "emotion_tags": {
            "items": [{"code": "UNSATISFIED", "name": "不满", "desc": "表达不满。"}],
        },
        "risk_tags": {
            "items": [{"code": "NORMAL", "name": "正常", "desc": "普通工单。"}],
        },
        "product_tags": {
            "items": [{"code": "MOBILE", "name": "移动业务", "desc": "手机业务。"}],
        },
    }

    fake_content = """
{
  "request_tag": {"code": "EXPLAIN", "reason": "用户要求解释收费原因"},
  "emotion_tag": {"code": "UNSATISFIED", "reason": "用户明显不认可"},
  "risk_tag": {"code": "NORMAL", "reason": "没有明显升级风险"},
  "product_tag": {"code": "MOBILE", "reason": "涉及手机直降礼包"},
  "resolution_summary": null
}
"""

    monkeypatch.setattr(analyze_controlled_tags_module, "load_runtime_data", lambda: runtime_data)
    monkeypatch.setattr(analyze_controlled_tags_module, "_create_openai_client", lambda: _FakeClient(fake_content))
    monkeypatch.setattr(
        analyze_controlled_tags_module,
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

    result = analyze_controlled_tags_module.analyze_controlled_tags(
        {
            "ticket": {
                "ticket_id": "T-2",
                "line_category": "市场条线",
                "biz_content": "用户不认可收费，要求解释。",
            },
            "primary_category": {
                "leaf_code": "PACKAGE_FEE_DISPUTE",
                "leaf_name": "套餐收费争议",
                "level1_code": "FEE_BILLING",
                "level1_name": "费用与账务",
                "level2_code": "PACKAGE_AND_USAGE_FEE",
                "level2_name": "套餐与使用费用",
            },
        }
    )

    assert result["status"] == "tags_selected"
    assert result["request_tag"]["code"] == "EXPLAIN"
    assert result["request_tag"]["name"] == "解释说明"
    assert result["emotion_tag"]["code"] == "UNSATISFIED"
    assert result["emotion_tag"]["name"] == "不满"
    assert result["risk_tag"]["code"] == "NORMAL"
    assert result["risk_tag"]["name"] == "正常"
    assert result["product_tag"]["code"] == "MOBILE"
    assert result["product_tag"]["name"] == "移动业务"
    assert result["line_category"]["value"] == "市场条线"
    assert "resolution_summary" not in result
