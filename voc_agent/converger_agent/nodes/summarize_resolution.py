from __future__ import annotations

from typing import Any, Mapping

from openai import OpenAI

from voc_agent.converger_agent.state import ConvergerState, ResolutionSummaryNodeOutput
from voc_agent.converger_agent.utils import build_summarize_resolution_messages
from voc_agent.core.config import get_settings
from voc_agent.share.utils import parse_json_payload_once

PROCESSING_FIELDS = [
    "return_reason",
    "prov_dispatch_desc",
    "prov_process_desc",
    "city_process_desc",
    "process_dept",
    "flow_depts",
]


def _create_openai_client() -> OpenAI:
    settings = get_settings()
    return OpenAI(base_url=settings.llm_base_url, api_key=settings.llm_api_key)


def _extract_response_text(response: Any) -> str:
    try:
        return response.choices[0].message.content or "{}"
    except Exception:
        return "{}"


def _has_processing_context(ticket: Mapping[str, Any]) -> bool:
    return any(ticket.get(field) not in (None, "", []) for field in PROCESSING_FIELDS)


def summarize_resolution(state: ConvergerState) -> ConvergerState:
    ticket = state["ticket"]
    if not _has_processing_context(ticket):
        return {
            "status": "resolution_unavailable",
            "resolution_summary": None,
        }

    settings = get_settings()
    client = _create_openai_client()
    messages = build_summarize_resolution_messages(
        ticket=ticket,
        primary_category=state["primary_category"],
        request_tag=state["request_tag"],
        product_tag=state["product_tag"],
    )

    response = client.chat.completions.create(
        model=settings.llm_model_name,
        temperature=settings.llm_temperature,
        messages=messages,
    )
    raw_text = _extract_response_text(response)
    raw_data = parse_json_payload_once(raw_text)
    parsed = ResolutionSummaryNodeOutput.model_validate(
        {"resolution_summary": raw_data.get("resolution_summary")}
    )
    return {
        "resolution_summary": parsed.resolution_summary,
        "status": "resolution_summarized" if parsed.resolution_summary else "resolution_unavailable",
        "resolution_prompt": messages[1]["content"],
        "resolution_raw_response": raw_text,
    }
