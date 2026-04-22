from __future__ import annotations

from voc_agent.converger_agent.utils.prompt_builder import (
    build_controlled_tags_messages,
    build_primary_category_messages,
)


def test_build_primary_category_messages_contains_ticket_and_rule_sections() -> None:
    runtime_data = {
        "category": {
            "disambiguation_rules": [
                {
                    "rule_id": "R01",
                    "when": "遇到承诺未兑现时按规则判断。",
                    "note": "优先归承诺未兑现。",
                }
            ],
            "level1": {
                "L1": {"name": "一级", "desc": "一级描述"},
            },
            "level2": {
                "L2": {
                    "parent_level1_code": "L1",
                    "name": "二级",
                    "desc": "二级描述",
                }
            },
            "leaves": {
                "LEAF_A": {
                    "parent_level1_code": "L1",
                    "parent_level2_code": "L2",
                    "name": "叶子A",
                    "desc": "叶子说明A",
                }
            },
        }
    }
    ticket = {
        "ticket_id": "T-1",
        "complaint_phenomenon": "收费问题",
        "biz_content": "用户不认可办理时未说明合约。",
    }

    messages = build_primary_category_messages(ticket, runtime_data)

    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert "【工单】" in messages[1]["content"]
    assert "【分类歧义规则】" in messages[1]["content"]
    assert "【可选分类叶子】" in messages[1]["content"]
    assert "T-1" in messages[1]["content"]
    assert "LEAF_A" in messages[1]["content"]


def test_build_controlled_tags_messages_contains_tag_sections_and_primary_category() -> None:
    runtime_data = {
        "request_tags": {
            "source_fields": ["complaint_phenomenon", "biz_content"],
            "selection_rule": "必须从常量中选 1 个。",
            "items": [{"code": "EXPLAIN", "name": "解释说明", "desc": "需要解释。"}],
        },
        "emotion_tags": {
            "source_fields": ["biz_content"],
            "selection_rule": "必须从常量中选 1 个。",
            "default_code": "CALM",
            "items": [{"code": "CALM", "name": "平稳", "desc": "情绪平稳。"}],
        },
        "risk_tags": {
            "source_fields": ["ticket_type"],
            "selection_rule": "必须从常量中选 1 个。",
            "default_code": "NORMAL",
            "items": [{"code": "NORMAL", "name": "正常", "desc": "普通工单。"}],
        },
        "product_tags": {
            "source_fields": ["dispute_product_name"],
            "selection_rule": "必须从常量中选 1 个。",
            "items": [{"code": "MOBILE", "name": "移动业务", "desc": "手机业务。"}],
        },
    }
    ticket = {
        "ticket_id": "T-2",
        "line_category": "市场条线",
        "biz_content": "用户要求解释收费原因。",
    }
    primary_category = {
        "level1_code": "FEE_BILLING",
        "level1_name": "费用与账务",
        "level2_code": "PACKAGE_AND_USAGE_FEE",
        "level2_name": "套餐与使用费用",
        "leaf_code": "PACKAGE_FEE_DISPUTE",
        "leaf_name": "套餐收费争议",
    }

    messages = build_controlled_tags_messages(ticket, primary_category, runtime_data)

    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert "【已确定主分类】" in messages[1]["content"]
    assert "PACKAGE_FEE_DISPUTE" in messages[1]["content"]
    assert "【可选 request_tag】" in messages[1]["content"]
    assert "【可选 emotion_tag】" in messages[1]["content"]
    assert "【可选 risk_tag】" in messages[1]["content"]
    assert "【可选 product_tag】" in messages[1]["content"]
    assert "市场条线" in messages[1]["content"]
