from __future__ import annotations

from voc_agent.advice_provider_agent.provider import mask_processing_context, rank_advice_candidates


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
