from __future__ import annotations

import json
from typing import Any


CATEGORY_CONFIDENCE_THRESHOLD = 0.75
TAG_CONFIDENCE_THRESHOLD = 0.7


CATEGORY_SYSTEM_PROMPT = """你是运营商投诉分类收敛 Agent。

你的任务是只判断一个最可信的主分类。

要求：
1. 只能从提供的分类清单中选择。
2. 只能返回一个主分类，不要返回多个候选分类。
3. 如果没有足够把握，请返回 null。
4. 只有当置信度不低于阈值时，这个分类才会被接受。
5. 输出必须是纯 JSON。

目标结构：
{
  "summary": "...",
  "primary_category": {
    "code": "分类编码",
    "full_name": "分类完整名称",
    "confidence": 0.0,
    "reason": "..."
  }
}"""


TAG_SYSTEM_PROMPT = """你是运营商投诉标签收敛 Agent。

你的任务是在已确认主分类的前提下，从标签清单中选择补充标签。

要求：
1. 每个标签组最多只能返回一个标签。
2. 没有把握的标签不要返回。
3. 输出必须是纯 JSON。

目标结构：
{
  "candidate_tags": [
    {
      "group_code": "标签组编码",
      "code": "标签编码",
      "name": "标签名称",
      "confidence": 0.0,
      "reason": "..."
    }
  ]
}"""


def _compact_ticket(ticket: dict[str, Any]) -> dict[str, Any]:
    keys = [
        'ticket_id',
        'ticket_type',
        'complaint_source',
        'biz_category',
        'line_category',
        'appeal_biz_type',
        'dispute_product_name',
        'accept_channel',
        'customer_group',
        'complaint_phenomenon',
        'biz_content',
        'return_reason',
        'prov_dispatch_desc',
        'prov_process_desc',
        'city_process_desc',
    ]
    return {key: ticket.get(key) for key in keys if ticket.get(key) not in (None, '')}


def build_category_prompt(ticket: dict[str, Any], categories: list[dict[str, Any]]) -> str:
    category_lines = []
    for item in categories:
        display = item.get('full_name') or item.get('name') or item.get('code')
        category_lines.append(f"- [{item['code']}] {display}")

    ticket_payload = json.dumps(_compact_ticket(ticket), ensure_ascii=False, indent=2)
    return f"""请只为下面工单判断一个最可信的主分类。

分类置信度阈值：{CATEGORY_CONFIDENCE_THRESHOLD}

【原始工单】
{ticket_payload}

【可选分类清单】
{chr(10).join(category_lines)}
"""


def build_tag_prompt(ticket: dict[str, Any], selected_category: dict[str, Any], tags: list[dict[str, Any]]) -> str:
    tag_lines = []
    for item in tags:
        tag_lines.append(f"- [{item['group_code']}] [{item['code']}] {item['name']}")

    ticket_payload = json.dumps(_compact_ticket(ticket), ensure_ascii=False, indent=2)
    category_payload = json.dumps(selected_category, ensure_ascii=False, indent=2)
    return f"""请在主分类已确定的前提下，为下面工单补充标签。

标签置信度阈值：{TAG_CONFIDENCE_THRESHOLD}
每个标签组最多只能保留一个标签。

【原始工单】
{ticket_payload}

【已确认主分类】
{category_payload}

【可选标签清单】
{chr(10).join(tag_lines)}
"""
