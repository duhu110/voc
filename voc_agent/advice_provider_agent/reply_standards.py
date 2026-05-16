from __future__ import annotations

import re
from typing import Any, Mapping


def build_reply_standards(ticket: Mapping[str, Any], classification: Mapping[str, Any]) -> list[dict[str, str]]:
    """Build deterministic reply/closure requirements from the strict ticket rules."""
    text = _combined_text(ticket, classification)
    standards: list[dict[str, str]] = []

    _add(
        standards,
        title="逐项回应用户诉求",
        content=(
            "回单需逐一回应用户投诉内容中的每个问题，并写清对应处理结果。"
            "涉及固话、宽带、手机等多个产品或多个诉求时，不得只回复其中一项。"
        ),
        applicability_note="所有工单均适用。",
    )
    _add(
        standards,
        title="处理结果与回单模板一致",
        content="回单内容必须与实际处理结果一致，避免模板与结果不符导致二次派单。",
        applicability_note="所有工单均适用。",
    )
    _add_time_limit_standard(standards, text)

    if _has_any(text, ("未联系上", "未联系到", "联系不上", "无人接听", "无法联系", "未接通")):
        _add(
            standards,
            title="未联系到用户后续跟踪",
            content=(
                "首次未联系到用户时，48小时内需在不同时间段联系3次，每次间隔2小时以上；"
                "使用集约平台外呼留痕。与用户协商后续处理或解决时限后，需持续跟踪并留痕。"
            ),
            applicability_note="命中未联系到用户或无法接通场景。",
        )

    if _has_any(text, ("未达成一致", "不认可", "不同意", "不接受", "无法达成一致", "无责")):
        _add(
            standards,
            title="未达成一致需补充依据",
            content=(
                "未与用户达成一致时，需补充企业无责或处理依据。"
                "可包括合规业务受理协议、业务办理实名拍照、回访录音、系统回访记录截图、主任签字等材料。"
            ),
            applicability_note="命中用户不认可、未达成一致或企业无责说明场景。",
        )

    if _is_refund_cancel_or_package_change(text):
        _add(
            standards,
            title="退订退费套餐变更回单",
            content=(
                "涉及退订、退费、套餐变更时，如问题已彻底解决，回单需添加对应流水号；"
                "退费类还需填写退费金额。如需发起工作流处理，需确认风险管控领导已同意工作流截图后再回单。"
            ),
            applicability_note="命中退订、退费、套餐变更或相关诉求标签。",
        )

    if _has_any(text, ("小合约", "预约拆机", "套餐变更", "单宽销户")):
        _add(
            standards,
            title="关键场景需最终结果",
            content="小合约、预约拆机无人联系、套餐变更、单宽销户场景，必须取得最终处理结果后再回单。",
            applicability_note="命中文档列明的必须有最终结果场景。",
        )

    if _has_any(text, ("约定时间", "预约时间", "约好", "约定", "承诺时间", "指定时间")):
        _add(
            standards,
            title="约定时间办理需附留痕",
            content="与用户约定时间办理时，附件需添加系统外呼截图及外呼录音。",
            applicability_note="命中与用户约定办理时间的场景。",
        )

    return standards


def _combined_text(ticket: Mapping[str, Any], classification: Mapping[str, Any]) -> str:
    values: list[str] = []
    for source in (ticket, classification):
        for value in source.values():
            if value is not None:
                values.append(str(value))
    return "\n".join(values)


def _add(
    standards: list[dict[str, str]],
    *,
    title: str,
    content: str,
    applicability_note: str,
) -> None:
    if any(item["title"] == title for item in standards):
        return
    standards.append(
        {
            "title": title,
            "content": content,
            "applicability_note": applicability_note,
        }
    )


def _add_time_limit_standard(standards: list[dict[str, str]], text: str) -> None:
    if "国际漫游" in text:
        _add(
            standards,
            title="集团回单时限",
            content="国际漫游投诉处理总时限为24小时，请优先跟进并按时回单。",
            applicability_note="命中国际漫游投诉来源或场景。",
        )
        return

    if _has_any(text, ("10005", "1005热线", "app投诉", "APP投诉", "新媒体客服", "互联网信息平台")):
        _add(
            standards,
            title="集团回单时限",
            content="10005热线、APP投诉、新媒体客服、互联网信息平台工单处理总时限为48小时。",
            applicability_note="命中集团通报归类中的48小时处理来源。",
        )


def _is_refund_cancel_or_package_change(text: str) -> bool:
    return _has_any(
        text,
        (
            "退订",
            "退费",
            "退款",
            "返费",
            "返还",
            "销户",
            "取消业务",
            "取消套餐",
            "套餐变更",
            "变更套餐",
            "改套餐",
            "更改套餐",
            "降档",
            "升档",
            "拆机",
            "REFUND",
            "CANCEL",
            "PACKAGE",
        ),
    )


def _has_any(text: str, terms: tuple[str, ...]) -> bool:
    lower_text = text.lower()
    return any(re.search(re.escape(term.lower()), lower_text) for term in terms)
