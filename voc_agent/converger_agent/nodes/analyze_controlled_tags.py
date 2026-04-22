from __future__ import annotations

from typing import Any, Mapping

from openai import OpenAI

from voc_agent.converger_agent.state import ControlledTagsNodeOutput, ConvergerState
from voc_agent.converger_agent.utils import build_controlled_tags_messages, load_runtime_data
from voc_agent.core.config import get_settings
from voc_agent.share.utils import parse_json_payload_once


def _create_openai_client() -> OpenAI:
    settings = get_settings()
    return OpenAI(base_url=settings.llm_base_url, api_key=settings.llm_api_key)


def _extract_response_text(response: Any) -> str:
    try:
        return response.choices[0].message.content or "{}"
    except Exception:
        return "{}"


def _resolve_tag(code: str, tag_group_data: Mapping[str, Any]) -> dict[str, str]:
    target = str(code).strip()
    for item in tag_group_data["items"]:
        if item["code"] == target:
            return {"code": item["code"], "name": item["name"]}
    raise ValueError(f"Unknown tag code returned by model: {target}")


def _normalize_controlled_tags(raw_data: Mapping[str, Any], ticket: Mapping[str, Any], runtime_data: Mapping[str, Any]) -> dict[str, Any]:
    request_tag = _resolve_tag(raw_data["request_tag"]["code"], runtime_data["request_tags"])
    emotion_tag = _resolve_tag(raw_data["emotion_tag"]["code"], runtime_data["emotion_tags"])
    risk_tag = _resolve_tag(raw_data["risk_tag"]["code"], runtime_data["risk_tags"])
    product_tag = _resolve_tag(raw_data["product_tag"]["code"], runtime_data["product_tags"])

    return {
        "request_tag": {
            **request_tag,
            "reason": str(raw_data["request_tag"].get("reason", "")).strip(),
        },
        "emotion_tag": {
            **emotion_tag,
            "reason": str(raw_data["emotion_tag"].get("reason", "")).strip(),
        },
        "risk_tag": {
            **risk_tag,
            "reason": str(raw_data["risk_tag"].get("reason", "")).strip(),
        },
        "product_tag": {
            **product_tag,
            "reason": str(raw_data["product_tag"].get("reason", "")).strip(),
        },
        "line_category": {
            "value": str(ticket.get("line_category", "")).strip(),
            "reason": "直接来自原始工单",
        },
    }


def analyze_controlled_tags(state: ConvergerState) -> ConvergerState:
    ticket = state["ticket"]
    primary_category = state["primary_category"]
    runtime_data = state.get("runtime_data") or load_runtime_data()
    settings = get_settings()
    client = _create_openai_client()
    messages = build_controlled_tags_messages(ticket, primary_category, runtime_data)

    response = client.chat.completions.create(
        model=settings.llm_model_name,
        temperature=settings.llm_temperature,
        messages=messages,
    )
    raw_text = _extract_response_text(response)
    raw_data = parse_json_payload_once(raw_text)
    normalized = _normalize_controlled_tags(raw_data, ticket, runtime_data)
    parsed = ControlledTagsNodeOutput.model_validate(normalized)

    return {
        "runtime_data": runtime_data,
        "request_tag": parsed.request_tag.model_dump(mode="json"),
        "emotion_tag": parsed.emotion_tag.model_dump(mode="json"),
        "risk_tag": parsed.risk_tag.model_dump(mode="json"),
        "product_tag": parsed.product_tag.model_dump(mode="json"),
        "line_category": parsed.line_category.model_dump(mode="json"),
        "status": "tags_selected",
        "tags_prompt": messages[1]["content"],
        "tags_raw_response": raw_text,
    }
