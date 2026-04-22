from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "voc_agent" / "converger_agent" / "data"

PROMPT_TICKET_FIELDS = [
    "id",
    "ticket_id",
    "ticket_type",
    "complaint_source",
    "biz_category",
    "line_category",
    "appeal_biz_type",
    "dispute_product_name",
    "customer_star",
    "repeat_count",
    "urge_count",
    "oscillation_count",
    "satisfaction_score",
    "complaint_phenomenon",
    "biz_content",
    "return_reason",
    "prov_dispatch_desc",
    "prov_process_desc",
    "city_process_desc",
    "process_dept",
    "flow_depts",
]


@dataclass(frozen=True)
class PromptSizeStats:
    system_chars: int
    user_chars: int
    total_chars: int
    system_lines: int
    user_lines: int
    total_lines: int


def _read_json(file_name: str) -> dict[str, Any]:
    path = DATA_DIR / file_name
    return json.loads(path.read_text(encoding="utf-8"))


def load_runtime_data() -> dict[str, Any]:
    return {
        "category": _read_json("category_v2.json"),
        "request_tags": _read_json("request_tags.json"),
        "emotion_tags": _read_json("emotion_tags.json"),
        "risk_tags": _read_json("risk_tags.json"),
        "product_tags": _read_json("product_tags.json"),
    }


def _json_safe(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def compact_ticket_for_prompt(ticket: Mapping[str, Any]) -> dict[str, Any]:
    compact: dict[str, Any] = {}
    for field in PROMPT_TICKET_FIELDS:
        value = ticket.get(field)
        if value in (None, "", []):
            continue
        compact[field] = _json_safe(value)
    return compact


def _build_disambiguation_rule_lines(category_data: Mapping[str, Any]) -> list[str]:
    lines: list[str] = []
    for rule in category_data["disambiguation_rules"]:
        note = rule.get("note")
        when = rule.get("when")
        if note and when:
            lines.append(f"- {rule['rule_id']}: {when} 规则说明：{note}")
        elif note:
            lines.append(f"- {rule['rule_id']}: {note}")
    return lines


def _build_category_lines(category_data: Mapping[str, Any]) -> list[str]:
    rows: list[tuple[str, str]] = []
    for leaf_code, leaf in category_data["leaves"].items():
        level1 = category_data["level1"][leaf["parent_level1_code"]]
        level2 = category_data["level2"][leaf["parent_level2_code"]]
        line = (
            f"- [{leaf['parent_level1_code']}] {level1['name']} / "
            f"[{leaf['parent_level2_code']}] {level2['name']} / "
            f"[{leaf_code}] {leaf['name']}：{leaf['desc']}"
        )
        rows.append((f"{leaf['parent_level1_code']}|{leaf['parent_level2_code']}|{leaf_code}", line))
    rows.sort(key=lambda item: item[0])
    return [line for _, line in rows]


def _build_tag_section(title: str, tag_data: Mapping[str, Any]) -> str:
    lines = [f"【{title}】"]
    source_fields = ", ".join(tag_data.get("source_fields", []))
    if source_fields:
        lines.append(f"重点参考字段：{source_fields}")
    selection_rule = tag_data.get("selection_rule")
    if selection_rule:
        lines.append(f"选择规则：{selection_rule}")
    default_code = tag_data.get("default_code")
    if default_code:
        lines.append(f"默认值：{default_code}")
    for item in tag_data["items"]:
        lines.append(f"- [{item['code']}] {item['name']}：{item['desc']}")
    return "\n".join(lines)


def build_converger_user_prompt(ticket: Mapping[str, Any], runtime_data: Mapping[str, Any]) -> str:
    category_data = runtime_data["category"]
    ticket_payload = json.dumps(compact_ticket_for_prompt(ticket), ensure_ascii=False, indent=2)

    sections = [
        "请基于下面工单信息，完成 converger_agent 的 7 项结构化分析。",
        "",
        "硬性要求：",
        "1. primary_category 必须且只能从给定 category_v2 叶子分类中选择 1 个。",
        "2. request_tag、emotion_tag、risk_tag、product_tag 必须且只能各选 1 个。",
        "3. line_category 不需要重新判断，直接沿用工单原值。",
        "4. resolution_summary 只有在工单已有处理信息且能提炼出可复用处理方法时才输出；否则为 null。",
        "5. 不允许输出给定范围之外的新分类或新标签。",
        "6. 只输出纯 JSON。",
        "",
        "返回 JSON 结构：",
        "{",
        '  "summary": "...",',
        '  "primary_category": {"level1_code": "...", "level1_name": "...", "level2_code": "...", "level2_name": "...", "leaf_code": "...", "leaf_name": "...", "reason": "..."},',
        '  "request_tag": {"code": "...", "name": "...", "reason": "..."},',
        '  "emotion_tag": {"code": "...", "name": "...", "reason": "..."},',
        '  "risk_tag": {"code": "...", "name": "...", "reason": "..."},',
        '  "line_category": {"value": "...", "reason": "直接来自原始工单"},',
        '  "product_tag": {"code": "...", "name": "...", "reason": "..."},',
        '  "resolution_summary": null',
        "}",
        "",
        "【工单】",
        ticket_payload,
        "",
        "【分类歧义规则】",
        *(_build_disambiguation_rule_lines(category_data) or ["- 无"]),
        "",
        "【可选分类叶子】",
        *_build_category_lines(category_data),
        "",
        _build_tag_section("可选 request_tag", runtime_data["request_tags"]),
        "",
        _build_tag_section("可选 emotion_tag", runtime_data["emotion_tags"]),
        "",
        _build_tag_section("可选 risk_tag", runtime_data["risk_tags"]),
        "",
        _build_tag_section("可选 product_tag", runtime_data["product_tags"]),
        "",
        "【line_category 处理规则】",
        "- 直接抄录原始工单中的 line_category 值。",
        "- 不做改写，不做重新分类。",
        "",
        "【resolution_summary 处理规则】",
        "- 只参考 return_reason、prov_dispatch_desc、prov_process_desc、city_process_desc、process_dept、flow_depts。",
        "- 只在已经有处理过程信息，且能提炼出对同类工单有指导性的处理结果或处理方法时输出。",
        "- 如果只是空泛表述、没有形成可复用经验，则返回 null。",
    ]
    return "\n".join(sections)


def build_primary_category_user_prompt(ticket: Mapping[str, Any], runtime_data: Mapping[str, Any]) -> str:
    category_data = runtime_data["category"]
    ticket_payload = json.dumps(compact_ticket_for_prompt(ticket), ensure_ascii=False, indent=2)
    sections = [
        "请只完成 primary_category 分析。",
        "",
        "硬性要求：",
        "1. 只能从给定 category_v2 叶子分类中选择 1 个。",
        "2. 必须优先遵守给定歧义规则。",
        "3. 不允许输出分类范围外的新值。",
        "4. 只输出纯 JSON。",
        "",
        "返回 JSON 结构：",
        "{",
        '  "summary": "...",',
        '  "level1_code": "...",',
        '  "level2_code": "...",',
        '  "leaf_code": "...",',
        '  "reason": "..."',
        "}",
        "",
        "【工单】",
        ticket_payload,
        "",
        "【分类歧义规则】",
        *(_build_disambiguation_rule_lines(category_data) or ["- 无"]),
        "",
        "【可选分类叶子】",
        *_build_category_lines(category_data),
    ]
    return "\n".join(sections)


def build_converger_messages(ticket: Mapping[str, Any], runtime_data: Mapping[str, Any] | None = None) -> list[dict[str, str]]:
    runtime = runtime_data or load_runtime_data()
    system_prompt = (
        "你是运营商投诉工单分析专家。\n\n"
        "你必须严格在给定分类与标签范围内完成结构化分析，不能自由发挥，不能生成范围外的新分类或新标签，输出只能是纯 JSON。"
    )
    user_prompt = build_converger_user_prompt(ticket, runtime)
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def build_primary_category_messages(
    ticket: Mapping[str, Any],
    runtime_data: Mapping[str, Any] | None = None,
) -> list[dict[str, str]]:
    runtime = runtime_data or load_runtime_data()
    system_prompt = (
        "你是运营商投诉分类专家。\n\n"
        "你只能在给定 category_v2 叶子分类中选择 1 个最合适的主分类，输出只能是纯 JSON。"
    )
    user_prompt = build_primary_category_user_prompt(ticket, runtime)
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def build_controlled_tags_user_prompt(
    ticket: Mapping[str, Any],
    primary_category: Mapping[str, Any],
    runtime_data: Mapping[str, Any],
) -> str:
    ticket_payload = json.dumps(compact_ticket_for_prompt(ticket), ensure_ascii=False, indent=2)
    primary_category_payload = json.dumps(primary_category, ensure_ascii=False, indent=2)
    sections = [
        "请在主分类已经确定的前提下，完成 request_tag、emotion_tag、risk_tag、product_tag、line_category 分析。",
        "",
        "硬性要求：",
        "1. request_tag、emotion_tag、risk_tag、product_tag 必须且只能各选 1 个。",
        "2. line_category 直接抄录原始工单值，不做重判。",
        "3. 只输出纯 JSON。",
        "",
        "返回 JSON 结构：",
        "{",
        '  "request_tag": {"code": "...", "reason": "..."},',
        '  "emotion_tag": {"code": "...", "reason": "..."},',
        '  "risk_tag": {"code": "...", "reason": "..."},',
        '  "product_tag": {"code": "...", "reason": "..."},',
        "}",
        "",
        "【已确定主分类】",
        primary_category_payload,
        "",
        "【工单】",
        ticket_payload,
        "",
        _build_tag_section("可选 request_tag", runtime_data["request_tags"]),
        "",
        _build_tag_section("可选 emotion_tag", runtime_data["emotion_tags"]),
        "",
        _build_tag_section("可选 risk_tag", runtime_data["risk_tags"]),
        "",
        _build_tag_section("可选 product_tag", runtime_data["product_tags"]),
        "",
        "【line_category 处理规则】",
        f"- 当前工单原始 line_category 为：{ticket.get('line_category', '')}",
        "- 直接抄录原始工单中的 line_category 值。",
    ]
    return "\n".join(sections)


def build_controlled_tags_messages(
    ticket: Mapping[str, Any],
    primary_category: Mapping[str, Any],
    runtime_data: Mapping[str, Any] | None = None,
) -> list[dict[str, str]]:
    runtime = runtime_data or load_runtime_data()
    system_prompt = (
        "你是运营商投诉工单分析专家。\n\n"
        "主分类已经给定。你必须严格在给定标签常量范围内选择 request_tag、emotion_tag、risk_tag、product_tag，并输出纯 JSON。"
    )
    user_prompt = build_controlled_tags_user_prompt(ticket, primary_category, runtime)
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def build_summarize_resolution_user_prompt(
    ticket: Mapping[str, Any],
    primary_category: Mapping[str, Any],
    request_tag: Mapping[str, Any],
    product_tag: Mapping[str, Any],
) -> str:
    ticket_payload = json.dumps(compact_ticket_for_prompt(ticket), ensure_ascii=False, indent=2)
    sections = [
        "请根据下面已确定的分类和标签，判断是否能总结出一条对同类工单有指导意义的处理结果或处理方法。",
        "",
        "硬性要求：",
        "1. 只参考 return_reason、prov_dispatch_desc、prov_process_desc、city_process_desc、process_dept、flow_depts。",
        "2. 只有在工单已有处理过程信息，且能提炼出可复用处理经验时才输出 resolution_summary。",
        "3. 如果没有足够处理信息，或者只能得到空泛描述，则返回 null。",
        "4. 只输出纯 JSON。",
        "",
        "返回 JSON 结构：",
        "{",
        '  "resolution_summary": null',
        "}",
        "",
        "【已确定主分类】",
        json.dumps(primary_category, ensure_ascii=False, indent=2),
        "",
        "【已确定 request_tag】",
        json.dumps(request_tag, ensure_ascii=False, indent=2),
        "",
        "【已确定 product_tag】",
        json.dumps(product_tag, ensure_ascii=False, indent=2),
        "",
        "【工单】",
        ticket_payload,
    ]
    return "\n".join(sections)


def build_summarize_resolution_messages(
    ticket: Mapping[str, Any],
    primary_category: Mapping[str, Any],
    request_tag: Mapping[str, Any],
    product_tag: Mapping[str, Any],
) -> list[dict[str, str]]:
    system_prompt = (
        "你是运营商投诉处理经验总结助手。\n\n"
        "你只能在工单已有明确处理过程信息时，提炼一条简洁且可复用的处理建议；否则返回 null。输出只能是纯 JSON。"
    )
    user_prompt = build_summarize_resolution_user_prompt(ticket, primary_category, request_tag, product_tag)
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def prompt_size_stats(messages: list[Mapping[str, str]]) -> PromptSizeStats:
    system_text = next((item["content"] for item in messages if item["role"] == "system"), "")
    user_text = next((item["content"] for item in messages if item["role"] == "user"), "")
    return PromptSizeStats(
        system_chars=len(system_text),
        user_chars=len(user_text),
        total_chars=len(system_text) + len(user_text),
        system_lines=system_text.count("\n") + (1 if system_text else 0),
        user_lines=user_text.count("\n") + (1 if user_text else 0),
        total_lines=(system_text.count("\n") + (1 if system_text else 0))
        + (user_text.count("\n") + (1 if user_text else 0)),
    )
