from __future__ import annotations

from importlib import import_module

analyze_primary_category_module = import_module("voc_agent.converger_agent.nodes.analyze_primary_category")


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


def test_analyze_primary_category_returns_mapped_leaf_details(monkeypatch) -> None:
    runtime_data = {
        "category": {
            "disambiguation_rules": [],
            "level1": {
                "FEE_BILLING": {"name": "费用与账务", "desc": "desc"},
            },
            "level2": {
                "PACKAGE_AND_USAGE_FEE": {
                    "parent_level1_code": "FEE_BILLING",
                    "name": "套餐与使用费用",
                    "desc": "desc",
                }
            },
            "leaves": {
                "PACKAGE_FEE_DISPUTE": {
                    "parent_level1_code": "FEE_BILLING",
                    "parent_level2_code": "PACKAGE_AND_USAGE_FEE",
                    "name": "套餐收费争议",
                    "desc": "对套餐收费不认可。",
                }
            },
        }
    }

    fake_content = """
{
  "summary": "用户对套餐收费不认可",
  "level1_code": "FEE_BILLING",
  "level2_code": "PACKAGE_AND_USAGE_FEE",
  "leaf_code": "PACKAGE_FEE_DISPUTE",
  "reason": "文本明确是套餐收费争议"
}
"""

    monkeypatch.setattr(analyze_primary_category_module, "load_runtime_data", lambda: runtime_data)
    monkeypatch.setattr(analyze_primary_category_module, "_create_openai_client", lambda: _FakeClient(fake_content))
    monkeypatch.setattr(
        analyze_primary_category_module,
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

    result = analyze_primary_category_module.analyze_primary_category(
        {
            "ticket": {
                "ticket_id": "T-1",
                "complaint_phenomenon": "收费问题",
                "biz_content": "用户不认可套餐收费。",
            }
        }
    )

    assert result["status"] == "category_selected"
    assert result["category_summary"] == "用户对套餐收费不认可"
    assert result["primary_category"]["level1_code"] == "FEE_BILLING"
    assert result["primary_category"]["level1_name"] == "费用与账务"
    assert result["primary_category"]["level2_code"] == "PACKAGE_AND_USAGE_FEE"
    assert result["primary_category"]["level2_name"] == "套餐与使用费用"
    assert result["primary_category"]["leaf_code"] == "PACKAGE_FEE_DISPUTE"
    assert result["primary_category"]["leaf_name"] == "套餐收费争议"
