from __future__ import annotations

from voc_agent.converger_agent.utils.result_rows import build_persistence_rows


def _sample_completed_result() -> dict:
    return {
        "ticket_id": "T-1",
        "status": "completed",
        "summary": "用户认为套餐收费规则不合理，要求解释。",
        "primary_category": {
            "level1_code": "FEE_BILLING",
            "level1_name": "费用与账务",
            "level2_code": "PACKAGE_AND_USAGE_FEE",
            "level2_name": "套餐与使用费用",
            "leaf_code": "PACKAGE_FEE_DISPUTE",
            "leaf_name": "套餐收费争议",
            "reason": "文本核心是套餐收费不认可。",
        },
        "request_tag": {"code": "EXPLAIN", "name": "解释说明", "reason": "要求解释收费规则。"},
        "emotion_tag": {"code": "UNSATISFIED", "name": "不满", "reason": "明显表达不满。"},
        "risk_tag": {"code": "NORMAL", "name": "正常", "reason": "普通工单。"},
        "product_tag": {"code": "MOBILE", "name": "移动业务", "reason": "涉及手机套餐。"},
        "line_category": {"value": "市场条线", "reason": "直接来自原始工单"},
        "resolution_summary": "先核对套餐生效时间，再补充收费规则解释。",
    }


def test_build_persistence_rows_for_completed_result() -> None:
    rows = build_persistence_rows(
        result=_sample_completed_result(),
        model_name="Qwen3-Max",
        taxonomy_version="v1",
        agent_version="v1",
    )

    assert rows["result_row"] == {
        "ticket_id": "T-1",
        "primary_level1_code": "FEE_BILLING",
        "primary_level1_name": "费用与账务",
        "primary_level2_code": "PACKAGE_AND_USAGE_FEE",
        "primary_level2_name": "套餐与使用费用",
        "primary_leaf_code": "PACKAGE_FEE_DISPUTE",
        "primary_leaf_name": "套餐收费争议",
        "request_tag_code": "EXPLAIN",
        "request_tag_name": "解释说明",
        "emotion_tag_code": "UNSATISFIED",
        "emotion_tag_name": "不满",
        "risk_tag_code": "NORMAL",
        "risk_tag_name": "正常",
        "product_tag_code": "MOBILE",
        "product_tag_name": "移动业务",
        "line_category": "市场条线",
        "model_name": "Qwen3-Max",
        "taxonomy_version": "v1",
        "agent_version": "v1",
        "status": "completed",
    }
    assert rows["resolution_summary_row"] == {
        "source_ticket_id": "T-1",
        "primary_leaf_code": "PACKAGE_FEE_DISPUTE",
        "primary_leaf_name": "套餐收费争议",
        "product_tag_code": "MOBILE",
        "product_tag_name": "移动业务",
        "request_tag_code": "EXPLAIN",
        "request_tag_name": "解释说明",
        "risk_tag_code": "NORMAL",
        "risk_tag_name": "正常",
        "emotion_tag_code": "UNSATISFIED",
        "emotion_tag_name": "不满",
        "line_category": "市场条线",
        "resolution_summary": "先核对套餐生效时间，再补充收费规则解释。",
        "model_name": "Qwen3-Max",
        "taxonomy_version": "v1",
        "agent_version": "v1",
        "status": "active",
    }


def test_build_persistence_rows_for_skipped_result() -> None:
    rows = build_persistence_rows(
        result={
            "ticket_id": "T-2",
            "status": "skipped_no_category",
            "stop_reason": "未命中可信分类",
        },
        model_name="Qwen3-Max",
        taxonomy_version="v1",
        agent_version="v1",
    )

    assert rows["result_row"] is None
    assert rows["resolution_summary_row"] is None
