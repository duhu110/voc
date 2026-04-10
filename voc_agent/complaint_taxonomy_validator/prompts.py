from __future__ import annotations

import json
from typing import Any


SYSTEM_PROMPT = """你是运营商投诉分类与标签体系验证 Agent。

你的任务不是回写数据库，也不是创造新分类，而是基于现有投诉分类树和标签体系，对单条原始工单做验证性判断。

要求：
1. 只能从提供的分类清单中选择分类。
2. 只能从提供的标签清单中选择标签。
3. 分类要优先选择最具体、最贴近投诉主诉的问题类目。
4. 标签是并行补充信息，不要把标签当分类。
5. category_keywords 和 tag_keywords 只提取对判断真正有帮助的关键词或短语。
6. 若信息不足，要在 risks 中明确写出不确定点。
7. 分类 code 和标签 code 必须严格使用清单里已有的真实编码，不允许自造编码。
8. 输出必须是纯 JSON 对象，不要使用 Markdown 代码块，不要附加解释文字。
9. 优先按以下目标结构输出：
{
  "summary": "...",
  "primary_category": {
    "code": "真实分类编码",
    "full_name": "真实分类完整名称",
    "confidence": 0.92,
    "reason": "..."
  },
  "candidate_categories": [],
  "candidate_tags": [],
  "category_keywords": [],
  "tag_keywords": [],
  "risks": []
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


def build_user_prompt(ticket: dict[str, Any], categories: list[dict[str, Any]], tags: list[dict[str, Any]]) -> str:
    category_lines = []
    for item in categories:
        display = item.get('full_name') or item.get('name') or item.get('code')
        extra = []
        if item.get('description'):
            extra.append(f"定义: {item['description']}")
        if item.get('keywords'):
            extra.append(f"典型关键词: {item['keywords']}")
        suffix = f" | {' ; '.join(extra)}" if extra else ''
        category_lines.append(f"- [{item['code']}] {display}{suffix}")

    tag_lines = []
    for item in tags:
        desc = f" | {item['description']}" if item.get('description') else ''
        tag_lines.append(f"- [{item['group_code']}] [{item['code']}] {item['name']}{desc}")

    ticket_payload = json.dumps(_compact_ticket(ticket), ensure_ascii=False, indent=2)

    return f"""请基于以下输入完成投诉分类与标签验证。

【原始工单】
{ticket_payload}

【可选分类清单】
{chr(10).join(category_lines)}

【可选标签清单】
{chr(10).join(tag_lines)}
"""
