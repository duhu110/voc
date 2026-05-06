from __future__ import annotations

import json
from typing import Any, Mapping

from sqlalchemy import text

from voc_agent.converger_agent.nodes.analyze_controlled_tags import analyze_controlled_tags
from voc_agent.converger_agent.nodes.analyze_primary_category import analyze_primary_category
from voc_agent.converger_agent.nodes.finalize_result import finalize_result
from voc_agent.converger_agent.utils import load_runtime_data
from voc_agent.core.db import get_engine
from voc_agent.share.tools import fetch_ticket


PROCESSING_FIELDS = [
    "return_reason",
    "prov_dispatch_desc",
    "prov_process_desc",
    "city_process_desc",
    "process_dept",
    "flow_depts",
]

EXISTING_RESULT_SQL = text(
    """
    select *
    from converger_agent_result
    where ticket_id = :ticket_id
    limit 1
    """
)

ADVICE_CANDIDATES_SQL = text(
    """
    select
      id,
      primary_leaf_code,
      primary_leaf_name,
      product_tag_code,
      product_tag_name,
      request_tag_code,
      request_tag_name,
      risk_tag_code,
      risk_tag_name,
      emotion_tag_code,
      emotion_tag_name,
      line_category,
      advice_title,
      advice_content,
      applicability_note,
      source_summary_count,
      latest_source_ticket_id,
      updated_at
    from converger_handling_advice
    where status = 'active'
      and primary_leaf_code = :primary_leaf_code
      and (
        coalesce(product_tag_code, '') = coalesce(:product_tag_code, '')
        or coalesce(request_tag_code, '') = coalesce(:request_tag_code, '')
        or (product_tag_code is null and request_tag_code is null)
      )
    """
)

SUMMARY_SAMPLE_SQL = text(
    """
    select
      source_ticket_id,
      primary_leaf_code,
      primary_leaf_name,
      product_tag_code,
      product_tag_name,
      request_tag_code,
      request_tag_name,
      risk_tag_name,
      emotion_tag_name,
      resolution_summary,
      created_at
    from converger_resolution_summary_atomic
    where status = 'active'
      and primary_leaf_code = :primary_leaf_code
      and coalesce(product_tag_code, '') = coalesce(:product_tag_code, '')
      and coalesce(request_tag_code, '') = coalesce(:request_tag_code, '')
      and (:exclude_ticket_id is null or source_ticket_id <> :exclude_ticket_id)
    order by created_at desc
    limit :limit
    """
)


def mask_processing_context(ticket: Mapping[str, Any]) -> dict[str, Any]:
    """Return a copy of a ticket without historical handling fields."""
    masked = dict(ticket)
    for field in PROCESSING_FIELDS:
        masked.pop(field, None)
    return masked


def _compact_advice(row: Mapping[str, Any], match_level: str) -> dict[str, Any]:
    return {
        "id": row["id"],
        "match_level": match_level,
        "primary_leaf_code": row["primary_leaf_code"],
        "primary_leaf_name": row["primary_leaf_name"],
        "product_tag_code": row.get("product_tag_code"),
        "product_tag_name": row.get("product_tag_name"),
        "request_tag_code": row.get("request_tag_code"),
        "request_tag_name": row.get("request_tag_name"),
        "advice_title": row["advice_title"],
        "advice_content": row["advice_content"],
        "applicability_note": row.get("applicability_note"),
        "source_summary_count": row["source_summary_count"],
        "latest_source_ticket_id": row.get("latest_source_ticket_id"),
    }


def rank_advice_candidates(
    rows: list[Mapping[str, Any]],
    *,
    product_tag_code: str | None,
    request_tag_code: str | None,
    limit: int,
) -> list[dict[str, Any]]:
    ranked: list[tuple[int, str, Mapping[str, Any]]] = []
    for row in rows:
        product_match = (row.get("product_tag_code") or "") == (product_tag_code or "")
        request_match = (row.get("request_tag_code") or "") == (request_tag_code or "")
        if product_match and request_match:
            score = 0
            level = "exact"
        elif product_match:
            score = 1
            level = "leaf_product"
        elif request_match:
            score = 2
            level = "leaf_request"
        else:
            score = 3
            level = "leaf"
        ranked.append((score, level, row))

    ranked.sort(key=lambda item: (item[0], -int(item[2].get("source_summary_count") or 0)))
    return [_compact_advice(row, level) for _, level, row in ranked[:limit]]


def _fetch_matching_advice(classification: Mapping[str, Any], limit: int) -> list[dict[str, Any]]:
    with get_engine().connect() as conn:
        rows = conn.execute(
            ADVICE_CANDIDATES_SQL,
            {
                "primary_leaf_code": classification["primary_leaf_code"],
                "product_tag_code": classification.get("product_tag_code"),
                "request_tag_code": classification.get("request_tag_code"),
            },
        ).mappings().all()
    return rank_advice_candidates(
        [dict(row) for row in rows],
        product_tag_code=classification.get("product_tag_code"),
        request_tag_code=classification.get("request_tag_code"),
        limit=limit,
    )


def _fetch_summary_samples(
    classification: Mapping[str, Any],
    *,
    exclude_ticket_id: str | None,
    limit: int,
) -> list[dict[str, Any]]:
    with get_engine().connect() as conn:
        rows = conn.execute(
            SUMMARY_SAMPLE_SQL,
            {
                "primary_leaf_code": classification["primary_leaf_code"],
                "product_tag_code": classification.get("product_tag_code"),
                "request_tag_code": classification.get("request_tag_code"),
                "exclude_ticket_id": exclude_ticket_id,
                "limit": limit,
            },
        ).mappings().all()
    return [dict(row) for row in rows]


def _classification_from_existing_result(ticket_id: str) -> dict[str, Any]:
    with get_engine().connect() as conn:
        row = conn.execute(EXISTING_RESULT_SQL, {"ticket_id": ticket_id}).mappings().first()
    if row is None:
        raise ValueError(f"No converger_agent_result found for ticket_id={ticket_id}")
    return {
        "primary_leaf_code": row["primary_leaf_code"],
        "primary_leaf_name": row["primary_leaf_name"],
        "product_tag_code": row["product_tag_code"],
        "product_tag_name": row["product_tag_name"],
        "request_tag_code": row["request_tag_code"],
        "request_tag_name": row["request_tag_name"],
        "risk_tag_code": row["risk_tag_code"],
        "risk_tag_name": row["risk_tag_name"],
        "emotion_tag_code": row["emotion_tag_code"],
        "emotion_tag_name": row["emotion_tag_name"],
        "line_category": row["line_category"],
    }


def _classification_from_converger(ticket: Mapping[str, Any]) -> dict[str, Any]:
    state: dict[str, Any] = {
        "ticket_id": str(ticket["ticket_id"]),
        "ticket": dict(ticket),
        "runtime_data": load_runtime_data(),
    }
    state.update(analyze_primary_category(state))
    state.update(analyze_controlled_tags(state))
    state.update(finalize_result(state))
    result = state["result"]
    primary_category = result["primary_category"]
    product_tag = result["product_tag"]
    request_tag = result["request_tag"]
    risk_tag = result["risk_tag"]
    emotion_tag = result["emotion_tag"]
    return {
        "primary_leaf_code": primary_category["leaf_code"],
        "primary_leaf_name": primary_category["leaf_name"],
        "product_tag_code": product_tag["code"],
        "product_tag_name": product_tag["name"],
        "request_tag_code": request_tag["code"],
        "request_tag_name": request_tag["name"],
        "risk_tag_code": risk_tag["code"],
        "risk_tag_name": risk_tag["name"],
        "emotion_tag_code": emotion_tag["code"],
        "emotion_tag_name": emotion_tag["name"],
        "line_category": result["line_category"]["value"],
    }


def _confidence(matched_advices: list[Mapping[str, Any]]) -> str:
    if not matched_advices:
        return "low"
    if matched_advices[0]["match_level"] == "exact":
        return "high"
    return "medium"


def _needs_human_review(classification: Mapping[str, Any], matched_advices: list[Mapping[str, Any]]) -> bool:
    risk_code = classification.get("risk_tag_code")
    emotion_code = classification.get("emotion_tag_code")
    if risk_code and risk_code != "NORMAL":
        return True
    if emotion_code in {"AGITATED", "ANGRY"}:
        return True
    if not matched_advices or matched_advices[0]["match_level"] != "exact":
        return True
    return False


def _risk_notes(classification: Mapping[str, Any], matched_advices: list[Mapping[str, Any]]) -> list[str]:
    notes: list[str] = []
    risk_name = classification.get("risk_tag_name")
    emotion_name = classification.get("emotion_tag_name")
    if classification.get("risk_tag_code") != "NORMAL":
        notes.append(f"风险标签为 {risk_name}，建议人工复核规则、证据和升级路径。")
    if classification.get("emotion_tag_code") in {"AGITATED", "ANGRY"}:
        notes.append(f"情绪标签为 {emotion_name}，建议优先安抚并加强回访确认。")
    if not matched_advices:
        notes.append("未命中处理建议库，需要人工给出处理方案或补充 advice。")
    elif matched_advices[0]["match_level"] != "exact":
        notes.append("未精确命中分类+产品+诉求组合，当前建议来自宽松匹配，需要人工确认适用性。")
    return notes


def run_advice_provider(
    ticket_id: str,
    *,
    use_existing_classification: bool = False,
    hide_processing_context: bool = True,
    advice_limit: int = 5,
    sample_limit: int = 5,
) -> dict[str, Any]:
    ticket = fetch_ticket(ticket_id)
    prompt_ticket = mask_processing_context(ticket) if hide_processing_context else dict(ticket)

    if use_existing_classification:
        classification = _classification_from_existing_result(ticket_id)
    else:
        classification = _classification_from_converger(prompt_ticket)

    matched_advices = _fetch_matching_advice(classification, limit=advice_limit)
    summary_samples = _fetch_summary_samples(
        classification,
        exclude_ticket_id=ticket_id,
        limit=sample_limit,
    )
    return {
        "ticket_id": ticket_id,
        "classification": classification,
        "matched_advices": matched_advices,
        "summary_samples": summary_samples,
        "recommended_actions": [
            {
                "title": item["advice_title"],
                "content": item["advice_content"],
                "applicability_note": item.get("applicability_note"),
                "match_level": item["match_level"],
            }
            for item in matched_advices
        ],
        "risk_notes": _risk_notes(classification, matched_advices),
        "confidence": _confidence(matched_advices),
        "needs_human_review": _needs_human_review(classification, matched_advices),
    }


def dumps_provider_result(result: Mapping[str, Any]) -> str:
    return json.dumps(result, ensure_ascii=False, indent=2, default=str)
