from __future__ import annotations

from types import SimpleNamespace

from chainlit_app import app as chainlit_app_module
from chainlit_app.app import (
    LATEST_EVIDENCE_ELEMENT_KEY,
    _build_supporting_elements,
    _format_primary_result,
    _remove_previous_evidence_element,
)


def test_primary_result_keeps_evidence_out_of_main_message() -> None:
    content = _format_primary_result(
        {
            "recommended_actions": [
                {
                    "title": "核实订购并处理退费",
                    "content": "核实订购凭证，确认后按规则处理，并同步解释费用产生原因。",
                    "applicability_note": "适用于用户否认订购并要求退费。",
                    "match_level": "exact",
                }
            ],
            "reply_standards": [
                {
                    "title": "逐项回应用户诉求",
                    "content": "回单必须逐项说明用户诉求、处理过程、处理结果和后续安排。",
                    "applicability_note": "所有工单均适用。",
                }
            ],
            "matched_advices": [{"advice_title": "不应出现在主消息"}],
            "summary_samples": [{"resolution_summary": "不应出现在主消息"}],
        }
    )

    assert "## 推荐处理动作" not in content
    assert "## 回单规范提醒" not in content
    assert "# 工单处理建议" not in content
    assert "命中依据" not in content
    assert "历史摘要样本" not in content
    assert "适用条件" not in content
    assert "match_level" not in content


def test_primary_result_limits_visible_actions() -> None:
    actions = [
        {"title": f"建议 {index}", "content": "处理步骤"}
        for index in range(1, 6)
    ]

    content = _format_primary_result({"recommended_actions": actions, "reply_standards": []})

    assert "建议 1" in content
    assert "建议 3" in content
    assert "建议 4" not in content
    assert "另有 2 条候选处理建议" in content


def test_primary_result_prefers_final_action_plan() -> None:
    content = _format_primary_result(
        {
            "final_action_plan": {
                "title": "宽带网速慢 / 网络修复处理方案",
                "steps": [
                    {"title": "先核实事实", "content": "查询套餐速率、测速记录和装维记录。"},
                    {"title": "执行处理动作", "content": "预约装维上门并明确完成时限。"},
                ],
                "reply_requirements": ["回单需写清测速结果和处理结果。"],
            },
            "recommended_actions": [
                {"title": "候选建议", "content": "不应作为主方案展开。"},
            ],
        }
    )

    assert "宽带网速慢 / 网络修复处理方案" in content
    assert "先核实事实" in content
    assert "回单要点" in content
    assert "候选建议" not in content
    assert "候选处理建议已放入" in content


def test_supporting_elements_use_single_side_panel(monkeypatch) -> None:
    monkeypatch.setattr(
        chainlit_app_module.cl,
        "CustomElement",
        lambda **kwargs: SimpleNamespace(**kwargs),
    )

    elements = _build_supporting_elements(
        {"ticket_id": "T-1", "biz_content": "用户要求退订彩铃业务"},
        {
            "ticket_id": "T-1",
            "classification": {},
            "risk_notes": [],
            "final_action_plan": {"title": "处理方案", "steps": []},
            "matched_advices": [],
            "summary_samples": [],
            "reply_standards": [{"title": "逐项回应用户诉求", "content": "逐项回应"}],
        },
    )

    assert len(elements) == 1
    assert elements[0].display == "side"
    assert elements[0].name == "EvidenceDetails"
    assert elements[0].props["replyStandards"][0]["title"] == "逐项回应用户诉求"
    assert elements[0].props["finalActionPlan"]["title"] == "处理方案"


def test_remove_previous_evidence_element(monkeypatch) -> None:
    calls: list[str] = []

    class FakeElement:
        async def remove(self) -> None:
            calls.append("removed")

    class FakeUserSession:
        def __init__(self) -> None:
            self.values = {LATEST_EVIDENCE_ELEMENT_KEY: FakeElement()}

        def get(self, key: str):
            return self.values.get(key)

        def set(self, key: str, value) -> None:
            self.values[key] = value

    fake_session = FakeUserSession()
    monkeypatch.setattr(chainlit_app_module.cl, "user_session", fake_session)

    import asyncio

    asyncio.run(_remove_previous_evidence_element())

    assert calls == ["removed"]
    assert fake_session.values[LATEST_EVIDENCE_ELEMENT_KEY] is None
