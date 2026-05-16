from __future__ import annotations

import asyncio
import datetime as dt
import sys
from pathlib import Path
from typing import Any, Mapping

import chainlit as cl

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from voc_agent.advice_provider_agent import run_advice_provider_for_ticket_payload
from voc_agent.advice_provider_agent.input_normalizer import (
    ImageInput,
    VisionModelError,
    normalize_user_input_to_ticket,
)
from chainlit_app.auth import is_valid_user

MAX_VISIBLE_ACTIONS = 3
MAX_VISIBLE_REPLY_STANDARDS = 6
MAX_ACTION_CHARS = 120
MAX_PLAN_STEP_CHARS = 220
LATEST_EVIDENCE_ELEMENT_KEY = "latest_evidence_element"


@cl.password_auth_callback
def auth_callback(username: str, password: str) -> cl.User | None:
    if not is_valid_user(username, password):
        return None
    return cl.User(identifier=username, metadata={"role": "operator"})


@cl.on_chat_start
async def on_chat_start() -> None:
    await cl.Message(
        content=(
            "请直接输入投诉描述，或上传包含投诉信息的截图。图片只会先转写/翻译成文字，"
            "分类、标签、处理建议和风险判断会继续由文本工单分析链路完成。"
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message) -> None:
    text = (message.content or "").strip()
    images = _extract_images(message)
    if not text and not images:
        await cl.Message(content="请补充投诉描述，或上传一张包含投诉信息的图片。").send()
        return

    progress = cl.Message(content="正在理解工单并检索处理建议...")
    await progress.send()

    try:
        ticket = await asyncio.to_thread(
            normalize_user_input_to_ticket,
            text=text,
            images=images,
        )
        result = await asyncio.to_thread(
            run_advice_provider_for_ticket_payload,
            ticket,
            hide_processing_context=True,
            advice_limit=MAX_VISIBLE_ACTIONS,
            sample_limit=5,
        )
    except VisionModelError as exc:
        progress.content = str(exc)
        await progress.update()
        return
    except Exception as exc:
        progress.content = f"处理失败：{exc}"
        await progress.update()
        return

    await _remove_previous_evidence_element()
    progress.content, progress.elements = _build_result_message(ticket, result)
    await progress.update()
    if progress.elements:
        cl.user_session.set(LATEST_EVIDENCE_ELEMENT_KEY, progress.elements[0])


def _extract_images(message: cl.Message) -> list[ImageInput]:
    images: list[ImageInput] = []
    for element in message.elements or []:
        path = getattr(element, "path", None)
        mime_type = getattr(element, "mime", None) or getattr(element, "mime_type", None)
        name = getattr(element, "name", None)
        if not path:
            continue
        path_obj = Path(path)
        suffix = path_obj.suffix.lower()
        is_image = (mime_type and str(mime_type).startswith("image/")) or suffix in {
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
            ".bmp",
        }
        if is_image:
            images.append(ImageInput(path=path_obj, mime_type=mime_type, name=name))
    return images


def _build_result_message(ticket: Mapping[str, Any], result: Mapping[str, Any]) -> tuple[str, list[Any]]:
    return _format_primary_result(result), _build_supporting_elements(ticket, result)


async def _remove_previous_evidence_element() -> None:
    previous = cl.user_session.get(LATEST_EVIDENCE_ELEMENT_KEY)
    if previous is None:
        return
    try:
        await previous.remove()
    finally:
        cl.user_session.set(LATEST_EVIDENCE_ELEMENT_KEY, None)


def _format_primary_result(result: Mapping[str, Any]) -> str:
    recommended_actions = result.get("recommended_actions") or []
    final_action_plan = result.get("final_action_plan") or {}

    lines: list[str] = []

    if final_action_plan:
        lines.extend(_format_final_action_plan(final_action_plan))
        if recommended_actions:
            lines.append("")
            lines.append(f"> 候选处理建议已放入“附加信息”，共 {len(recommended_actions)} 条。")
    elif recommended_actions:
        visible_actions = recommended_actions[:MAX_VISIBLE_ACTIONS]
        for index, action in enumerate(visible_actions, start=1):
            lines.extend(
                [
                    f"{index}. **{_value(action.get('title'))}**",
                    f"   - {_compact_text(action.get('content'), max_chars=MAX_ACTION_CHARS)}",
                ]
            )
        hidden_count = len(recommended_actions) - len(visible_actions)
        if hidden_count > 0:
            lines.append(f"> 另有 {hidden_count} 条候选处理建议已放入“附加信息”。")
    else:
        lines.append("- 暂未命中处理建议库，请人工制定方案并补充建议沉淀。")

    if result.get("needs_human_review"):
        lines.extend(["", "> 当前结果建议人工复核后再回单。"])

    return "\n".join(lines)


def _format_final_action_plan(plan: Mapping[str, Any]) -> list[str]:
    lines = [f"**{_value(plan.get('title'), empty='处理方案')}**"]
    steps = plan.get("steps") or []
    for index, step in enumerate(steps, start=1):
        if not isinstance(step, Mapping):
            continue
        title = _value(step.get("title"))
        content = _compact_text(step.get("content"), max_chars=MAX_PLAN_STEP_CHARS)
        lines.extend([f"{index}. **{title}**", f"   - {content}"])

    requirements = plan.get("reply_requirements") or []
    if requirements:
        lines.append("")
        lines.append("**回单要点**")
        for item in requirements[:2]:
            lines.append(f"- {_compact_text(item, max_chars=MAX_PLAN_STEP_CHARS)}")
    return lines


def _build_supporting_elements(ticket: Mapping[str, Any], result: Mapping[str, Any]) -> list[Any]:
    classification = result.get("classification") or {}
    return [
        cl.CustomElement(
            name="EvidenceDetails",
            props={
                "ticket": _jsonable(
                    {
                        "ticketId": result.get("ticket_id", ticket.get("ticket_id", "")),
                        "complaintPhenomenon": ticket.get("complaint_phenomenon"),
                        "bizContent": ticket.get("biz_content"),
                        "lineCategory": ticket.get("line_category") or "未提供",
                    }
                ),
                "classification": _jsonable(
                    {
                        "primary": _pair_value(classification, "primary_leaf_name", "primary_leaf_code"),
                        "product": _pair_value(classification, "product_tag_name", "product_tag_code"),
                        "request": _pair_value(classification, "request_tag_name", "request_tag_code"),
                        "risk": _pair_value(classification, "risk_tag_name", "risk_tag_code"),
                        "emotion": _pair_value(classification, "emotion_tag_name", "emotion_tag_code"),
                        "confidence": result.get("confidence", "-"),
                        "needsHumanReview": bool(result.get("needs_human_review")),
                    }
                ),
                "riskNotes": _jsonable(result.get("risk_notes") or []),
                "finalActionPlan": _jsonable(result.get("final_action_plan") or {}),
                "replyStandards": _jsonable(result.get("reply_standards") or []),
                "matchedAdvices": _jsonable(result.get("matched_advices") or []),
                "expertPlaybooks": _jsonable(result.get("expert_playbooks") or []),
                "summarySamples": _jsonable(result.get("summary_samples") or []),
            },
            display="side",
        )
    ]


def _value(value: Any, *, empty: str = "-") -> str:
    text = str(value or "").strip()
    return text if text else empty


def _pair(data: Mapping[str, Any], name_key: str, code_key: str) -> str:
    name = _value(data.get(name_key))
    code = _value(data.get(code_key))
    return f"{name} (`{code}`)"


def _pair_value(data: Mapping[str, Any], name_key: str, code_key: str) -> dict[str, str]:
    return {
        "name": _value(data.get(name_key)),
        "code": _value(data.get(code_key)),
    }


def _compact_text(value: Any, *, max_chars: int) -> str:
    text = " ".join(_value(value).split())
    if len(text) <= max_chars:
        return text
    return f"{text[: max_chars - 1].rstrip()}..."


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, dt.datetime):
        return value.isoformat()
    if isinstance(value, dt.date):
        return value.isoformat()
    return value
