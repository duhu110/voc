from __future__ import annotations

import re
from typing import Any, Mapping


PHASES = (
    ("verify", "先核实事实", ("核实事实", "核实")),
    ("judge", "判断规则和责任", ("判断规则", "判断")),
    ("execute", "执行处理动作", ("执行动作", "处理方案", "执行")),
    ("callback", "回访和回单要求", ("回访确认", "回访", "回单")),
)


def build_final_action_plan(
    *,
    ticket: Mapping[str, Any],
    classification: Mapping[str, Any],
    recommended_actions: list[Mapping[str, Any]],
    reply_standards: list[Mapping[str, Any]],
    risk_notes: list[str],
) -> dict[str, Any]:
    """Turn candidate advice into one operator-facing handling plan."""
    primary_name = _value(classification.get("primary_leaf_name"), "投诉")
    request_name = _value(classification.get("request_tag_name"), "处理")
    title = f"{primary_name} / {request_name}处理方案"
    action_texts = [str(item.get("content") or "").strip() for item in recommended_actions[:2]]
    phase_contents = _collect_phase_contents(action_texts)

    steps = [
        {
            "title": phase_title,
            "content": phase_contents.get(key) or _fallback_phase_content(key, ticket, classification),
        }
        for key, phase_title, _ in PHASES
    ]

    if risk_notes:
        steps.append(
            {
                "title": "人工复核重点",
                "content": "；".join(_compact_text(note, max_chars=120) for note in risk_notes[:3]),
            }
        )

    reply_requirements = [
        _compact_text(str(item.get("content") or item.get("title") or ""), max_chars=140)
        for item in reply_standards[:3]
        if item.get("content") or item.get("title")
    ]

    return {
        "title": title,
        "steps": steps,
        "reply_requirements": reply_requirements,
        "source_action_titles": [
            str(item.get("title") or "").strip()
            for item in recommended_actions[:3]
            if item.get("title")
        ],
    }


def _collect_phase_contents(action_texts: list[str]) -> dict[str, str]:
    collected: dict[str, list[str]] = {key: [] for key, _, _ in PHASES}
    for text in action_texts:
        sections = _split_numbered_sections(text)
        if not sections:
            sections = [text]
        for section in sections:
            normalized = _compact_text(section, max_chars=360)
            if not normalized:
                continue
            phase_key = _phase_for_section(normalized)
            if phase_key and normalized not in collected[phase_key]:
                collected[phase_key].append(normalized)

    return {
        key: "；".join(items[:2])
        for key, items in collected.items()
        if items
    }


def _split_numbered_sections(text: str) -> list[str]:
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not cleaned:
        return []
    matches = list(re.finditer(r"(?:^|\n)\s*\d+[.、]\s*", cleaned))
    if not matches:
        return []
    sections: list[str] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(cleaned)
        label_start = match.start()
        section = cleaned[label_start:end].strip()
        section = re.sub(r"^\d+[.、]\s*", "", section)
        sections.append(section)
    return sections


def _phase_for_section(section: str) -> str | None:
    stripped = section.lstrip()
    for key, _, markers in PHASES:
        if any(stripped.startswith(marker) for marker in markers):
            return key
    return None


def _fallback_phase_content(key: str, ticket: Mapping[str, Any], classification: Mapping[str, Any]) -> str:
    scenario = _scenario_fallback(key, classification)
    if scenario:
        return scenario

    primary_name = _value(classification.get("primary_leaf_name"), "当前问题")
    product_name = _value(classification.get("product_tag_name"), "相关业务")
    request_name = _value(classification.get("request_tag_name"), "用户诉求")
    if key == "verify":
        return f"围绕{primary_name}核实用户号码、业务状态、历史工单、系统记录和用户原始诉求，确认问题是否属实。"
    if key == "judge":
        return f"结合{product_name}规则、系统记录和用户证据，判断责任归属、是否可直接办理以及是否需要升级复核。"
    if key == "execute":
        return f"按{request_name}诉求给出可执行处理：能办理的明确系统动作、责任部门和完成时限；不能办理的说明规则依据和替代路径。"
    return "处理完成后回访用户确认结果；未达成一致时，回单需写清核实依据、处理过程、无法满足的原因和后续跟踪安排。"


def _scenario_fallback(key: str, classification: Mapping[str, Any]) -> str:
    leaf_code = str(classification.get("primary_leaf_code") or "")
    request_code = str(classification.get("request_tag_code") or "")

    if leaf_code == "ORDER_DENIAL":
        return {
            "verify": "查询订购流水、办理渠道、验证码/二次确认、协议或录音、扣费账期、当前业务状态和历史退订记录。",
            "judge": "判断是否存在有效订购凭证和充分告知；无有效凭证、营销解释不清或用户明确否认时，按争议业务处理。",
            "execute": "先退订或拦截后续扣费；符合退费规则的登记退费金额和到账时限，不符合的说明证据依据并给出后续取消路径。",
            "callback": "回访时逐项说明订购证据、退订结果、退费金额或不退费依据；未达成一致时补充协议、录音、流水截图等材料。",
        }.get(key, "")

    if leaf_code == "OUT_OF_BUNDLE_FEE_DISPUTE":
        return {
            "verify": "调取流量/通话详单、套餐余量、超套计费规则、短信提醒发送记录、主副卡使用记录和前期工单结论。",
            "judge": "判断费用是否按套餐规则正常产生、提醒是否成功发送、是否存在系统计费异常或用户首次争议可协商空间。",
            "execute": "计费异常则修正并退费；计费正常则解释规则、提醒记录和费用构成，必要时提供流量包、套餐变更或一次性关怀申请路径。",
            "callback": "回单写清超套金额、提醒记录、规则依据和是否退费；用户不认可时标注升级风险并附系统证据。",
        }.get(key, "")

    if leaf_code == "RISK_MODEL_SHUTDOWN_DISPUTE":
        return {
            "verify": "查询停机类型、停机时间、号码状态、风险等级、复机权限、用户所在地和前期复机处理记录。",
            "judge": "判断是否属于高风险双停、公安/反诈/模型管控或资料不合规，并确认线上、异地或归属地营业厅复机规则。",
            "execute": "能复机的按权限办理；无权限线上复机的，明确归属地或异地有权限营业厅路径，特殊困难场景上报网信安/市场接口复核。",
            "callback": "向用户说明停机依据、复机材料、办理地点和时限；未达成一致时记录已解释权限边界和升级处理结果。",
        }.get(key, "")

    if leaf_code in {"PLAN_CHANGE_DISPUTE", "DELIVERY_DELAY", "INSTALL_MOVE_URGING"} or request_code == "CHANGE_PLAN":
        return {
            "verify": "查询预约单、在途工单、套餐/合约状态、拆装机状态、设备安装或归还情况、用户要求完成的具体时间。",
            "judge": "判断卡点是装维未履约、在途工单未竣工、合约限制、设备条件未满足、前台无权限还是套餐变更规则限制。",
            "execute": "明确责任部门并催办竣工或取消在途工单；可变更的安排营业厅、远程柜台或客户经理办理，涉及费用争议同步核查账期责任。",
            "callback": "按约定时间主动回访，确认是否已上门、拆机、装机或套餐变更成功；未完成不得只解释结单。",
        }.get(key, "")

    if leaf_code in {"CANCEL_FAILURE", "CANCEL_DISPUTE"}:
        return {
            "verify": "查询业务状态、退订入口、系统报错、合约限制、在途订单、销售品依赖关系和是否已产生费用。",
            "judge": "判断退订失败原因属于系统异常、规则限制、前台无权限、合约未到期还是资料/状态不满足。",
            "execute": "系统异常转后台支撑并跟踪结果；规则限制需说明解除条件；可退订的立即办理并同步后续费用影响。",
            "callback": "回访确认业务已退订或失败原因已说明，回单写清报错、处理流水、完成时间和后续费用口径。",
        }.get(key, "")

    return ""


def _value(value: Any, default: str) -> str:
    text = str(value or "").strip()
    return text if text else default


def _compact_text(value: str, *, max_chars: int) -> str:
    text = re.sub(r"\s+", " ", value).strip(" ；;")
    text = re.sub(r"^\d+[.、]\s*", "", text)
    if len(text) <= max_chars:
        return text
    return f"{text[: max_chars - 1].rstrip()}..."
