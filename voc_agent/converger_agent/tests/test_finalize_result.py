from __future__ import annotations

from importlib import import_module

finalize_result_module = import_module("voc_agent.converger_agent.nodes.finalize_result")


def test_finalize_result_collects_final_output() -> None:
    state = {
        "ticket_id": "T-1",
        "status": "tags_selected",
        "category_summary": "用户对套餐收费不认可",
        "primary_category": {
            "level1_code": "FEE_BILLING",
            "level1_name": "费用与账务",
            "level2_code": "PACKAGE_AND_USAGE_FEE",
            "level2_name": "套餐与使用费用",
            "leaf_code": "PACKAGE_FEE_DISPUTE",
            "leaf_name": "套餐收费争议",
            "reason": "收费争议",
        },
        "request_tag": {"code": "EXPLAIN", "name": "解释说明", "reason": "要求解释"},
        "emotion_tag": {"code": "UNSATISFIED", "name": "不满", "reason": "明显不满"},
        "risk_tag": {"code": "NORMAL", "name": "正常", "reason": "普通工单"},
        "product_tag": {"code": "MOBILE", "name": "移动业务", "reason": "涉及移动业务"},
        "line_category": {"value": "市场条线", "reason": "直接来自原始工单"},
        "resolution_summary": None,
    }

    result = finalize_result_module.finalize_result(state)

    assert result["result"]["ticket_id"] == "T-1"
    assert result["result"]["status"] == "completed"
    assert result["result"]["summary"] == "用户对套餐收费不认可"
    assert result["result"]["primary_category"]["leaf_code"] == "PACKAGE_FEE_DISPUTE"
    assert result["result"]["request_tag"]["code"] == "EXPLAIN"
    assert result["result"]["resolution_summary"] is None


def test_finalize_result_marks_skipped_when_no_category() -> None:
    result = finalize_result_module.finalize_result(
        {
            "ticket_id": "T-2",
            "status": "skipped_no_category",
            "stop_reason": "未命中可信分类",
        }
    )

    assert result["result"]["ticket_id"] == "T-2"
    assert result["result"]["status"] == "skipped_no_category"
    assert result["result"]["stop_reason"] == "未命中可信分类"

