from __future__ import annotations

import json
from typing import Any, Mapping

from sqlalchemy import text

from voc_agent.converger_agent.nodes.analyze_controlled_tags import analyze_controlled_tags
from voc_agent.converger_agent.nodes.analyze_primary_category import analyze_primary_category
from voc_agent.converger_agent.nodes.finalize_result import finalize_result
from voc_agent.converger_agent.utils import load_runtime_data
from voc_agent.advice_provider_agent.reply_standards import build_reply_standards
from voc_agent.advice_provider_agent.action_plan import build_final_action_plan
from voc_agent.advice_provider_agent.experience_playbooks import (
    build_experience_playbooks,
    build_general_experience_fallback,
)
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
      and (
        cast(:exclude_ticket_id as varchar) is null
        or source_ticket_id <> cast(:exclude_ticket_id as varchar)
      )
    order by created_at desc
    limit :limit
    """
)

EXPERT_PLAYBOOK_SQL = text(
    """
    select
      id,
      scenario_key,
      title,
      source_case_no,
      source_case_title,
      trigger_keywords,
      primary_leaf_code,
      primary_leaf_name,
      product_tag_code,
      product_tag_name,
      request_tag_code,
      request_tag_name,
      verify_steps,
      judgment_rules,
      execution_steps,
      callback_requirements,
      communication_tips,
      priority,
      updated_at
    from expert_handling_playbook
    where status = 'active'
      and review_status = 'reviewed'
      and (
        primary_leaf_code = :primary_leaf_code
        or coalesce(product_tag_code, '') = coalesce(:product_tag_code, '')
        or coalesce(request_tag_code, '') = coalesce(:request_tag_code, '')
        or primary_leaf_code is null
      )
    order by priority asc, updated_at desc
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


def _fetch_expert_playbooks(
    ticket: Mapping[str, Any],
    classification: Mapping[str, Any],
    *,
    limit: int,
) -> list[dict[str, Any]]:
    with get_engine().connect() as conn:
        rows = conn.execute(
            EXPERT_PLAYBOOK_SQL,
            {
                "primary_leaf_code": classification["primary_leaf_code"],
                "product_tag_code": classification.get("product_tag_code"),
                "request_tag_code": classification.get("request_tag_code"),
                "limit": max(limit * 8, 20),
            },
        ).mappings().all()

    scored: list[tuple[int, int, dict[str, Any]]] = []
    search_text = _search_text(ticket, classification)
    for row in rows:
        item = dict(row)
        keywords = item.get("trigger_keywords") or []
        keyword_score = sum(1 for keyword in keywords if keyword and str(keyword).lower() in search_text)
        class_score = 0
        primary_match = item.get("primary_leaf_code") == classification.get("primary_leaf_code")
        if primary_match:
            class_score += 4
        if item.get("product_tag_code") == classification.get("product_tag_code"):
            class_score += 2
        if item.get("request_tag_code") == classification.get("request_tag_code"):
            class_score += 1
        if not primary_match and keyword_score < 2:
            continue
        total_score = class_score + keyword_score
        if total_score <= 0:
            continue
        scored.append((-total_score, int(item.get("priority") or 100), item))

    scored.sort(key=lambda entry: (entry[0], entry[1]))
    return [item for _, _, item in scored[:limit]]


def _search_text(ticket: Mapping[str, Any], classification: Mapping[str, Any]) -> str:
    values: list[str] = []
    for source in (ticket, classification):
        for value in source.values():
            if value is not None:
                values.append(str(value))
    return "\n".join(values).lower()


def _expert_actions(rows: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    for row in rows:
        title = str(row.get("source_case_title") or row.get("title") or "专家处理剧本")
        content = _format_expert_action_content(row)
        actions.append(
            {
                "title": f"专家案例：{title}",
                "content": content,
                "applicability_note": "来自专家处理案例库，需结合当前工单证据确认适用性。",
                "match_level": "expert_playbook",
                "source_case_no": row.get("source_case_no"),
                "scenario_key": row.get("scenario_key"),
            }
        )
    return actions


def _format_expert_action_content(row: Mapping[str, Any]) -> str:
    sections = [
        ("核实事实", row.get("verify_steps") or []),
        ("判断规则", row.get("judgment_rules") or []),
        ("执行动作", row.get("execution_steps") or []),
        ("回访确认", row.get("callback_requirements") or []),
    ]
    lines: list[str] = []
    for index, (title, values) in enumerate(sections, start=1):
        text = "；".join(str(item).strip() for item in list(values)[:2] if str(item).strip())
        if text:
            lines.append(f"{index}. {title}：{text}")
    return "\n".join(lines)


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


def _confidence(
    matched_advices: list[Mapping[str, Any]],
    experience_actions: list[Mapping[str, Any]] | None = None,
) -> str:
    if not matched_advices:
        return "medium" if experience_actions else "low"
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


def _risk_notes(
    classification: Mapping[str, Any],
    matched_advices: list[Mapping[str, Any]],
    experience_actions: list[Mapping[str, Any]] | None = None,
) -> list[str]:
    notes: list[str] = []
    risk_name = classification.get("risk_tag_name")
    emotion_name = classification.get("emotion_tag_name")
    if classification.get("risk_tag_code") != "NORMAL":
        notes.append(f"风险标签为 {risk_name}，建议人工复核规则、证据和升级路径。")
    if classification.get("emotion_tag_code") in {"AGITATED", "ANGRY"}:
        notes.append(f"情绪标签为 {emotion_name}，建议优先安抚并加强回访确认。")
    if not matched_advices:
        if experience_actions:
            notes.append("未命中处理建议库，已补充本地经验剧本，需要人工确认适用性并沉淀 advice。")
        else:
            notes.append("未命中处理建议库，需要人工给出处理方案或补充 advice。")
    elif matched_advices[0]["match_level"] != "exact":
        notes.append("未精确命中分类+产品+诉求组合，当前建议来自宽松匹配，需要人工确认适用性。")
    return notes


def _recommended_actions(
    matched_advices: list[Mapping[str, Any]],
    supplemental_actions: list[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = [
        {
            "title": item["advice_title"],
            "content": item["advice_content"],
            "applicability_note": item.get("applicability_note"),
            "match_level": item["match_level"],
        }
        for item in matched_advices
    ]
    existing_titles = {item["title"] for item in actions}
    for item in supplemental_actions:
        title = str(item["title"])
        if title in existing_titles:
            continue
        actions.append(
            {
                "title": title,
                "content": item["content"],
                "applicability_note": item.get("applicability_note"),
                "match_level": item.get("match_level", "experience_playbook"),
            }
        )
        existing_titles.add(title)
    return actions


def run_advice_provider(
    ticket_id: str,
    *,
    use_existing_classification: bool = False,
    hide_processing_context: bool = True,
    advice_limit: int = 5,
    sample_limit: int = 5,
) -> dict[str, Any]:
    ticket = fetch_ticket(ticket_id)
    return _run_advice_provider_for_ticket(
        ticket,
        use_existing_classification=use_existing_classification,
        hide_processing_context=hide_processing_context,
        advice_limit=advice_limit,
        sample_limit=sample_limit,
    )


def run_advice_provider_for_ticket_payload(
    ticket: Mapping[str, Any],
    *,
    hide_processing_context: bool = True,
    advice_limit: int = 5,
    sample_limit: int = 5,
) -> dict[str, Any]:
    """Provide advice for a transient ticket payload without reading or writing a ticket row."""
    if not ticket.get("ticket_id"):
        raise ValueError("ticket payload must include ticket_id")
    return _run_advice_provider_for_ticket(
        dict(ticket),
        use_existing_classification=False,
        hide_processing_context=hide_processing_context,
        advice_limit=advice_limit,
        sample_limit=sample_limit,
    )


def _run_advice_provider_for_ticket(
    ticket: Mapping[str, Any],
    *,
    use_existing_classification: bool,
    hide_processing_context: bool,
    advice_limit: int,
    sample_limit: int,
) -> dict[str, Any]:
    ticket_id = str(ticket["ticket_id"])
    prompt_ticket = mask_processing_context(ticket) if hide_processing_context else dict(ticket)

    if use_existing_classification:
        classification = _classification_from_existing_result(ticket_id)
    else:
        classification = _classification_from_converger(prompt_ticket)

    matched_advices = _fetch_matching_advice(classification, limit=advice_limit)
    expert_playbooks = _fetch_expert_playbooks(prompt_ticket, classification, limit=2)
    expert_actions = _expert_actions(expert_playbooks)
    experience_actions = build_experience_playbooks(prompt_ticket, classification)
    supplemental_actions = [*expert_actions, *experience_actions]
    if not matched_advices and not supplemental_actions:
        supplemental_actions = [build_general_experience_fallback()]
    summary_samples = _fetch_summary_samples(
        classification,
        exclude_ticket_id=ticket_id,
        limit=sample_limit,
    )
    reply_standards = build_reply_standards(prompt_ticket, classification)
    recommended_actions = _recommended_actions(matched_advices, supplemental_actions)
    risk_notes = _risk_notes(classification, matched_advices, supplemental_actions)
    final_action_plan = build_final_action_plan(
        ticket=prompt_ticket,
        classification=classification,
        recommended_actions=recommended_actions,
        reply_standards=reply_standards,
        risk_notes=risk_notes,
    )
    return {
        "ticket_id": ticket_id,
        "classification": classification,
        "matched_advices": matched_advices,
        "expert_playbooks": expert_playbooks,
        "expert_actions": expert_actions,
        "experience_actions": experience_actions,
        "summary_samples": summary_samples,
        "recommended_actions": recommended_actions,
        "final_action_plan": final_action_plan,
        "reply_standards": reply_standards,
        "risk_notes": risk_notes,
        "confidence": _confidence(matched_advices, supplemental_actions),
        "needs_human_review": _needs_human_review(classification, matched_advices),
    }


def dumps_provider_result(result: Mapping[str, Any]) -> str:
    return json.dumps(result, ensure_ascii=False, indent=2, default=str)
