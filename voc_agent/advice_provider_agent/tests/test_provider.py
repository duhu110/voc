from __future__ import annotations

from voc_agent.advice_provider_agent import provider
from voc_agent.advice_provider_agent.provider import (
    mask_processing_context,
    rank_advice_candidates,
    run_advice_provider_for_ticket_payload,
)
from voc_agent.advice_provider_agent.reply_standards import build_reply_standards


def test_mask_processing_context_removes_handling_fields() -> None:
    ticket = {
        "ticket_id": "T-1",
        "biz_content": "用户投诉费用问题",
        "return_reason": "已处理",
        "prov_process_desc": "已退费",
    }

    masked = mask_processing_context(ticket)

    assert masked == {
        "ticket_id": "T-1",
        "biz_content": "用户投诉费用问题",
    }


def test_rank_advice_candidates_prefers_exact_match_then_source_count() -> None:
    rows = [
        {
            "id": 1,
            "primary_leaf_code": "ORDER_DENIAL",
            "primary_leaf_name": "用户否认订购",
            "product_tag_code": "VALUE_ADDED",
            "product_tag_name": "增值业务",
            "request_tag_code": "CANCEL",
            "request_tag_name": "取消业务",
            "advice_title": "宽松诉求",
            "advice_content": "解释并处理。",
            "applicability_note": None,
            "source_summary_count": 999,
            "latest_source_ticket_id": "A",
        },
        {
            "id": 2,
            "primary_leaf_code": "ORDER_DENIAL",
            "primary_leaf_name": "用户否认订购",
            "product_tag_code": "VALUE_ADDED",
            "product_tag_name": "增值业务",
            "request_tag_code": "REFUND",
            "request_tag_name": "退费",
            "advice_title": "精确退费",
            "advice_content": "核实后退订退费。",
            "applicability_note": "需核实证据。",
            "source_summary_count": 100,
            "latest_source_ticket_id": "B",
        },
    ]

    ranked = rank_advice_candidates(
        rows,
        product_tag_code="VALUE_ADDED",
        request_tag_code="REFUND",
        limit=2,
    )

    assert ranked[0]["id"] == 2
    assert ranked[0]["match_level"] == "exact"
    assert ranked[1]["id"] == 1
    assert ranked[1]["match_level"] == "leaf_product"


def test_run_advice_provider_for_ticket_payload_does_not_fetch_raw_ticket(monkeypatch) -> None:
    def fake_classification(ticket):
        return {
            "primary_leaf_code": "ORDER_DENIAL",
            "primary_leaf_name": "用户否认订购",
            "product_tag_code": "VALUE_ADDED",
            "product_tag_name": "增值业务",
            "request_tag_code": "REFUND",
            "request_tag_name": "退费",
            "risk_tag_code": "NORMAL",
            "risk_tag_name": "普通风险",
            "emotion_tag_code": "CALM",
            "emotion_tag_name": "平静",
            "line_category": "",
        }

    def fail_fetch_ticket(ticket_id):
        raise AssertionError("temporary payload must not fetch raw_complaint_tickets")

    monkeypatch.setattr(provider, "fetch_ticket", fail_fetch_ticket)
    monkeypatch.setattr(provider, "_classification_from_converger", fake_classification)
    monkeypatch.setattr(
        provider,
        "_fetch_matching_advice",
        lambda classification, limit: [
            {
                "id": 1,
                "match_level": "exact",
                "primary_leaf_code": "ORDER_DENIAL",
                "primary_leaf_name": "用户否认订购",
                "product_tag_code": "VALUE_ADDED",
                "product_tag_name": "增值业务",
                "request_tag_code": "REFUND",
                "request_tag_name": "退费",
                "advice_title": "核实订购并处理退费",
                "advice_content": "核实订购凭证，确认后按规则处理。",
                "applicability_note": "适用于用户否认订购并要求退费。",
                "source_summary_count": 20,
                "latest_source_ticket_id": "T-OLD",
            }
        ],
    )
    monkeypatch.setattr(provider, "_fetch_expert_playbooks", lambda ticket, classification, limit: [])
    monkeypatch.setattr(provider, "_fetch_summary_samples", lambda classification, exclude_ticket_id, limit: [])

    result = run_advice_provider_for_ticket_payload(
        {
            "ticket_id": "ui-test",
            "biz_content": "用户否认订购增值业务，要求退费。",
            "complaint_phenomenon": "否认订购",
            "line_category": "",
        }
    )

    assert result["ticket_id"] == "ui-test"
    assert result["confidence"] == "high"
    assert result["needs_human_review"] is False
    assert result["recommended_actions"][0]["title"] == "核实订购并处理退费"
    assert result["final_action_plan"]["title"] == "用户否认订购 / 退费处理方案"
    assert result["final_action_plan"]["steps"][0]["title"] == "先核实事实"
    assert any(item["title"] == "退订退费套餐变更回单" for item in result["reply_standards"])


def test_run_advice_provider_adds_experience_playbook_when_advice_misses(monkeypatch) -> None:
    def fake_classification(ticket):
        return {
            "primary_leaf_code": "BROADBAND_SLOW",
            "primary_leaf_name": "宽带网速慢",
            "product_tag_code": "BROADBAND",
            "product_tag_name": "宽带业务",
            "request_tag_code": "REPAIR_NETWORK",
            "request_tag_name": "网络修复",
            "risk_tag_code": "NORMAL",
            "risk_tag_name": "普通风险",
            "emotion_tag_code": "UNSATISFIED",
            "emotion_tag_name": "不满",
            "line_category": "",
        }

    monkeypatch.setattr(provider, "_classification_from_converger", fake_classification)
    monkeypatch.setattr(provider, "_fetch_matching_advice", lambda classification, limit: [])
    monkeypatch.setattr(provider, "_fetch_expert_playbooks", lambda ticket, classification, limit: [])
    monkeypatch.setattr(provider, "_fetch_summary_samples", lambda classification, exclude_ticket_id, limit: [])

    result = run_advice_provider_for_ticket_payload(
        {
            "ticket_id": "ui-broadband",
            "biz_content": "用户反映宽带网速慢，测速不达标，要求解决。",
            "complaint_phenomenon": "宽带网速慢",
            "line_category": "",
        }
    )

    assert result["confidence"] == "medium"
    assert result["needs_human_review"] is True
    assert result["recommended_actions"][0]["title"] == "宽带网速慢/不稳定闭环处理"
    assert result["recommended_actions"][0]["match_level"] == "experience_playbook"
    assert result["final_action_plan"]["steps"][2]["title"] == "执行处理动作"
    assert any("本地经验剧本" in item for item in result["risk_notes"])


def test_run_advice_provider_adds_appointment_playbook_when_delivery_misses(monkeypatch) -> None:
    def fake_classification(ticket):
        return {
            "primary_leaf_code": "DELIVERY_DELAY",
            "primary_leaf_name": "履约不及时/未履约",
            "product_tag_code": "BROADBAND",
            "product_tag_name": "宽带业务",
            "request_tag_code": "CHANGE_PLAN",
            "request_tag_name": "变更套餐",
            "risk_tag_code": "NORMAL",
            "risk_tag_name": "普通风险",
            "emotion_tag_code": "UNSATISFIED",
            "emotion_tag_name": "不满",
            "line_category": "",
        }

    monkeypatch.setattr(provider, "_classification_from_converger", fake_classification)
    monkeypatch.setattr(provider, "_fetch_matching_advice", lambda classification, limit: [])
    monkeypatch.setattr(provider, "_fetch_expert_playbooks", lambda ticket, classification, limit: [])
    monkeypatch.setattr(provider, "_fetch_summary_samples", lambda classification, exclude_ticket_id, limit: [])

    result = run_advice_provider_for_ticket_payload(
        {
            "ticket_id": "ui-delivery",
            "biz_content": "用户预约拆机后未办理，要求今天上门拆机并同步变更套餐。",
            "complaint_phenomenon": "宽带预约拆机处理不及时",
            "line_category": "",
        }
    )

    assert result["recommended_actions"][0]["title"] == "预约装拆移机/履约不及时处理"
    assert "套餐变更" in result["recommended_actions"][0]["content"]


def test_run_advice_provider_uses_expert_playbook_when_available(monkeypatch) -> None:
    def fake_classification(ticket):
        return {
            "primary_leaf_code": "ORDER_DENIAL",
            "primary_leaf_name": "用户否认订购",
            "product_tag_code": "VALUE_ADDED",
            "product_tag_name": "增值业务",
            "request_tag_code": "REFUND",
            "request_tag_name": "退费",
            "risk_tag_code": "NORMAL",
            "risk_tag_name": "普通风险",
            "emotion_tag_code": "CALM",
            "emotion_tag_name": "平静",
            "line_category": "",
        }

    monkeypatch.setattr(provider, "_classification_from_converger", fake_classification)
    monkeypatch.setattr(provider, "_fetch_matching_advice", lambda classification, limit: [])
    monkeypatch.setattr(
        provider,
        "_fetch_expert_playbooks",
        lambda ticket, classification, limit: [
            {
                "scenario_key": "expert_case_001",
                "source_case_no": 1,
                "source_case_title": "专家否认订购案例",
                "verify_steps": ["查询订购流水和录音"],
                "judgment_rules": ["判断是否有有效订购凭证"],
                "execution_steps": ["无凭证则退订退费"],
                "callback_requirements": ["回访说明退费金额和到账时间"],
            }
        ],
    )
    monkeypatch.setattr(provider, "_fetch_summary_samples", lambda classification, exclude_ticket_id, limit: [])

    result = run_advice_provider_for_ticket_payload(
        {
            "ticket_id": "ui-expert",
            "biz_content": "用户否认订购增值业务，要求退费。",
            "complaint_phenomenon": "用户否认订购",
            "line_category": "",
        }
    )

    assert result["confidence"] == "medium"
    assert result["recommended_actions"][0]["title"] == "专家案例：专家否认订购案例"
    assert result["recommended_actions"][0]["match_level"] == "expert_playbook"
    assert result["expert_playbooks"][0]["source_case_no"] == 1


def test_build_reply_standards_applies_strict_ticket_rules() -> None:
    standards = build_reply_standards(
        {
            "ticket_id": "T-2",
            "complaint_source": "10005热线",
            "biz_content": "用户未联系到，要求退费并套餐变更，用户不认可处理方案。",
        },
        {
            "request_tag_code": "REFUND",
            "request_tag_name": "退费",
            "product_tag_name": "套餐",
        },
    )

    titles = {item["title"] for item in standards}

    assert "逐项回应用户诉求" in titles
    assert "集团回单时限" in titles
    assert "未联系到用户后续跟踪" in titles
    assert "未达成一致需补充依据" in titles
    assert "退订退费套餐变更回单" in titles
    assert "关键场景需最终结果" in titles
    assert any("48小时" in item["content"] for item in standards if item["title"] == "集团回单时限")
