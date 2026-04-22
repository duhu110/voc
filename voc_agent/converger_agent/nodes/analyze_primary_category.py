from __future__ import annotations

from typing import Any, Mapping

from openai import OpenAI

from voc_agent.converger_agent.state import ConvergerState, PrimaryCategoryNodeOutput
from voc_agent.converger_agent.utils import build_primary_category_messages, load_runtime_data
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


def _normalize_primary_category(raw_data: Mapping[str, Any], category_data: Mapping[str, Any]) -> dict[str, Any]:
    leaf_code = str(raw_data.get("leaf_code", "")).strip()
    if not leaf_code:
        raise ValueError("Missing leaf_code in primary category response")
    leaf = category_data["leaves"].get(leaf_code)
    if leaf is None:
        raise ValueError(f"Unknown leaf_code returned by model: {leaf_code}")

    level2_code = leaf["parent_level2_code"]
    level1_code = leaf["parent_level1_code"]
    level2 = category_data["level2"][level2_code]
    level1 = category_data["level1"][level1_code]

    return {
        "summary": str(raw_data.get("summary", "")).strip(),
        "primary_category": {
            "level1_code": level1_code,
            "level1_name": level1["name"],
            "level2_code": level2_code,
            "level2_name": level2["name"],
            "leaf_code": leaf_code,
            "leaf_name": leaf["name"],
            "reason": str(raw_data.get("reason", "")).strip(),
        },
    }


def analyze_primary_category(state: ConvergerState) -> ConvergerState:
    ticket = state["ticket"]
    runtime_data = state.get("runtime_data") or load_runtime_data()
    settings = get_settings()
    client = _create_openai_client()
    messages = build_primary_category_messages(ticket, runtime_data)

    response = client.chat.completions.create(
        model=settings.llm_model_name,
        temperature=settings.llm_temperature,
        messages=messages,
    )
    raw_text = _extract_response_text(response)
    raw_data = parse_json_payload_once(raw_text)
    normalized = _normalize_primary_category(raw_data, runtime_data["category"])
    parsed = PrimaryCategoryNodeOutput.model_validate(normalized)

    return {
        "runtime_data": runtime_data,
        "category_summary": parsed.summary,
        "primary_category": parsed.primary_category.model_dump(mode="json"),
        "status": "category_selected",
        "category_prompt": messages[1]["content"],
        "category_raw_response": raw_text,
    }
