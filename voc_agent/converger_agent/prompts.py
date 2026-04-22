from __future__ import annotations

from voc_agent.converger_agent.utils.prompt_builder import (
    build_converger_messages,
    build_converger_user_prompt,
    load_runtime_data,
)

SYSTEM_PROMPT = """你是运营商投诉工单分析专家。

你的任务不是自由总结，而是严格依据给定的分类体系和标签常量，完成一条工单的结构化收敛分析。

硬性要求：
1. primary_category 必须且只能从给定的 category_v2.json 叶子分类中选择 1 个。
2. request_tag、emotion_tag、risk_tag、product_tag 必须且只能从各自给定常量中选择 1 个。
3. line_category 不需要重新判断，应直接沿用原始工单中的 line_category 值。
4. resolution_summary 只在工单已有处理信息且能提炼出可复用处理方法时输出；否则返回 null。
5. 遇到边界相近的分类时，优先遵守给定的歧义规则。
6. 只能输出纯 JSON，不要输出 Markdown，不要输出解释性前后缀。
"""

OUTPUT_SCHEMA_NOTE = """返回 JSON 结构：
{
  "summary": "对工单的简短概括",
  "primary_category": {
    "level1_code": "一级编码",
    "level1_name": "一级名称",
    "level2_code": "二级编码",
    "level2_name": "二级名称",
    "leaf_code": "叶子编码",
    "leaf_name": "叶子名称",
    "reason": "分类理由"
  },
  "request_tag": {
    "code": "诉求标签编码",
    "name": "诉求标签名称",
    "reason": "选择理由"
  },
  "emotion_tag": {
    "code": "情绪标签编码",
    "name": "情绪标签名称",
    "reason": "选择理由"
  },
  "risk_tag": {
    "code": "风险标签编码",
    "name": "风险标签名称",
    "reason": "选择理由"
  },
  "line_category": {
    "value": "原始工单中的 line_category",
    "reason": "固定写：直接来自原始工单"
  },
  "product_tag": {
    "code": "产品标签编码",
    "name": "产品标签名称",
    "reason": "选择理由"
  },
  "resolution_summary": "处理结果或处理方法总结，没有则为 null"
}
"""

__all__ = [
    "SYSTEM_PROMPT",
    "OUTPUT_SCHEMA_NOTE",
    "load_runtime_data",
    "build_converger_user_prompt",
    "build_converger_messages",
]
