from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any

from openai import OpenAI
from sqlalchemy import text

from voc_agent.core.config import get_settings
from voc_agent.core.db import get_engine
from voc_agent.share.utils import parse_json_payload_once


TOP_SCOPES_SQL = text(
    """
    with scope_counts as (
      select
        primary_leaf_code,
        primary_leaf_name,
        product_tag_code,
        product_tag_name,
        request_tag_code,
        request_tag_name,
        count(*) as summary_count,
        max(created_at) as latest_created_at
      from converger_resolution_summary_atomic
      where status = 'active'
        and resolution_summary is not null
        and btrim(resolution_summary) <> ''
      group by
        primary_leaf_code,
        primary_leaf_name,
        product_tag_code,
        product_tag_name,
        request_tag_code,
        request_tag_name
    )
    select *
    from scope_counts s
    where s.summary_count >= :min_summary_count
      and (
        :skip_existing = false
        or not exists (
          select 1
          from converger_handling_advice a
          where a.status = 'active'
            and a.primary_leaf_code = s.primary_leaf_code
            and coalesce(a.product_tag_code, '') = coalesce(s.product_tag_code, '')
            and coalesce(a.request_tag_code, '') = coalesce(s.request_tag_code, '')
        )
      )
    order by s.summary_count desc, s.latest_created_at desc
    limit :limit
    """
)

SCOPE_SAMPLES_SQL = text(
    """
    select
      source_ticket_id,
      risk_tag_code,
      risk_tag_name,
      emotion_tag_code,
      emotion_tag_name,
      line_category,
      resolution_summary,
      created_at
    from converger_resolution_summary_atomic
    where status = 'active'
      and primary_leaf_code = :primary_leaf_code
      and coalesce(product_tag_code, '') = coalesce(:product_tag_code, '')
      and coalesce(request_tag_code, '') = coalesce(:request_tag_code, '')
      and resolution_summary is not null
      and btrim(resolution_summary) <> ''
    order by created_at desc
    limit :sample_size
    """
)

ADVICE_UPSERT_SQL = text(
    """
    insert into converger_handling_advice (
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
      normalized_advice_hash,
      source_summary_count,
      latest_source_ticket_id,
      status
    ) values (
      :primary_leaf_code,
      :primary_leaf_name,
      :product_tag_code,
      :product_tag_name,
      :request_tag_code,
      :request_tag_name,
      :risk_tag_code,
      :risk_tag_name,
      :emotion_tag_code,
      :emotion_tag_name,
      :line_category,
      :advice_title,
      :advice_content,
      :applicability_note,
      :normalized_advice_hash,
      :source_summary_count,
      :latest_source_ticket_id,
      'active'
    )
    on conflict (
      primary_leaf_code,
      coalesce(product_tag_code, ''),
      coalesce(request_tag_code, ''),
      normalized_advice_hash
    )
    do update set
      advice_title = excluded.advice_title,
      advice_content = excluded.advice_content,
      applicability_note = excluded.applicability_note,
      source_summary_count = greatest(
        converger_handling_advice.source_summary_count,
        excluded.source_summary_count
      ),
      latest_source_ticket_id = excluded.latest_source_ticket_id,
      updated_at = current_timestamp,
      status = 'active'
    """
)


@dataclass(frozen=True)
class BuilderSummary:
    scanned_scopes: int
    generated_advice: int
    written_advice: int
    failed_scopes: int


def normalize_advice_text(value: str) -> str:
    text_value = re.sub(r"\s+", " ", value.strip().lower())
    return text_value


def build_advice_hash(title: str, content: str, applicability_note: str | None = None) -> str:
    normalized = "\n".join(
        [
            normalize_advice_text(title),
            normalize_advice_text(content),
            normalize_advice_text(applicability_note or ""),
        ]
    )
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _create_openai_client() -> OpenAI:
    settings = get_settings()
    return OpenAI(base_url=settings.llm_base_url, api_key=settings.llm_api_key)


def _fetch_top_scopes(limit: int, min_summary_count: int, skip_existing: bool) -> list[dict[str, Any]]:
    with get_engine().connect() as conn:
        rows = conn.execute(
            TOP_SCOPES_SQL,
            {
                "limit": limit,
                "min_summary_count": min_summary_count,
                "skip_existing": skip_existing,
            },
        ).mappings().all()
    return [dict(row) for row in rows]


def _fetch_scope_samples(scope: dict[str, Any], sample_size: int) -> list[dict[str, Any]]:
    with get_engine().connect() as conn:
        rows = conn.execute(
            SCOPE_SAMPLES_SQL,
            {
                "primary_leaf_code": scope["primary_leaf_code"],
                "product_tag_code": scope.get("product_tag_code"),
                "request_tag_code": scope.get("request_tag_code"),
                "sample_size": sample_size,
            },
        ).mappings().all()
    return [dict(row) for row in rows]


def _build_messages(scope: dict[str, Any], samples: list[dict[str, Any]]) -> list[dict[str, str]]:
    compact_samples = [
        {
            "source_ticket_id": item["source_ticket_id"],
            "risk_tag_name": item.get("risk_tag_name"),
            "emotion_tag_name": item.get("emotion_tag_name"),
            "line_category": item.get("line_category"),
            "resolution_summary": item.get("resolution_summary"),
        }
        for item in samples
    ]
    scope_payload = {
        "primary_leaf_code": scope["primary_leaf_code"],
        "primary_leaf_name": scope["primary_leaf_name"],
        "product_tag_code": scope.get("product_tag_code"),
        "product_tag_name": scope.get("product_tag_name"),
        "request_tag_code": scope.get("request_tag_code"),
        "request_tag_name": scope.get("request_tag_name"),
        "source_summary_count": int(scope["summary_count"]),
    }
    user_prompt = "\n".join(
        [
            "请基于同一投诉场景下的历史处理摘要，归纳可复用处理建议。",
            "",
            "要求：",
            "1. 输出 1 到 3 条建议，建议必须能指导新工单处理。",
            "2. 不要编造政策、金额、时限、系统能力；只归纳样本中稳定出现的处理方法。",
            "3. 如果样本只说明已联系、已解释、用户认可，也要提炼成可执行步骤。",
            "4. advice_content 写成客服/处理人员可直接参考的步骤。",
            "5. applicability_note 写适用条件、例外情况或需要人工核实的点。",
            "6. 只输出纯 JSON。",
            "7. 不允许输出具体退费金额、到账时限、违约金减免结论、合约解除结论，除非样本中对该场景高度一致且明确；否则必须写成“按本地规则核实/申请/告知”。",
            "8. 对涉及退费、违约金、合约、实名、监管、停复机的内容，必须增加“需人工核实规则和证据”的适用说明。",
            "9. 建议内容要分成：核实事实 -> 判断规则 -> 执行动作 -> 回访确认，不要把个案处理方式写成通用承诺。",
            "10. 不要输出具体套餐名、优惠包名、第三方产品补偿方案、具体到账时限；如果样本出现，只能写成“按本地可用方案处理/协调业务方核实”。",
            "",
            "返回 JSON：",
            "{",
            '  "advices": [',
            '    {"advice_title": "...", "advice_content": "...", "applicability_note": "..."}',
            "  ]",
            "}",
            "",
            "【场景】",
            json.dumps(scope_payload, ensure_ascii=False, indent=2, default=str),
            "",
            "【历史处理摘要样本】",
            json.dumps(compact_samples, ensure_ascii=False, indent=2, default=str),
        ]
    )
    return [
        {
            "role": "system",
            "content": "你是运营商投诉处理经验归纳专家，只能从历史处理摘要中归纳稳健、可执行的处理建议，输出纯 JSON。",
        },
        {"role": "user", "content": user_prompt},
    ]


def _call_model(messages: list[dict[str, str]]) -> dict[str, Any]:
    settings = get_settings()
    client = _create_openai_client()
    response = client.chat.completions.create(
        model=settings.llm_model_name,
        temperature=settings.llm_temperature,
        messages=messages,
    )
    content = response.choices[0].message.content or "{}"
    return parse_json_payload_once(content)


def _coerce_advices(raw_data: dict[str, Any]) -> list[dict[str, str]]:
    raw_advices = raw_data.get("advices")
    if not isinstance(raw_advices, list):
        return []
    advices: list[dict[str, str]] = []
    for item in raw_advices[:3]:
        if not isinstance(item, dict):
            continue
        title = str(item.get("advice_title") or "").strip()
        content = str(item.get("advice_content") or "").strip()
        applicability_note = str(item.get("applicability_note") or "").strip()
        if not title or not content:
            continue
        advices.append(
            {
                "advice_title": title[:255],
                "advice_content": content,
                "applicability_note": applicability_note,
            }
        )
    return advices


def _build_advice_rows(
    *,
    scope: dict[str, Any],
    samples: list[dict[str, Any]],
    advices: list[dict[str, str]],
) -> list[dict[str, Any]]:
    latest_source_ticket_id = samples[0]["source_ticket_id"] if samples else None
    rows: list[dict[str, Any]] = []
    for advice in advices:
        rows.append(
            {
                "primary_leaf_code": scope["primary_leaf_code"],
                "primary_leaf_name": scope["primary_leaf_name"],
                "product_tag_code": scope.get("product_tag_code"),
                "product_tag_name": scope.get("product_tag_name"),
                "request_tag_code": scope.get("request_tag_code"),
                "request_tag_name": scope.get("request_tag_name"),
                "risk_tag_code": None,
                "risk_tag_name": None,
                "emotion_tag_code": None,
                "emotion_tag_name": None,
                "line_category": None,
                "advice_title": advice["advice_title"],
                "advice_content": advice["advice_content"],
                "applicability_note": advice.get("applicability_note") or None,
                "normalized_advice_hash": build_advice_hash(
                    advice["advice_title"],
                    advice["advice_content"],
                    advice.get("applicability_note"),
                ),
                "source_summary_count": int(scope["summary_count"]),
                "latest_source_ticket_id": latest_source_ticket_id,
            }
        )
    return rows


def _write_advice_rows(rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0
    with get_engine().begin() as conn:
        for row in rows:
            conn.execute(ADVICE_UPSERT_SQL, row)
    return len(rows)


def build_advice_for_top_scopes(
    *,
    limit: int,
    min_summary_count: int,
    sample_size: int,
    dry_run: bool = True,
    skip_existing: bool = True,
) -> BuilderSummary:
    scopes = _fetch_top_scopes(
        limit=limit,
        min_summary_count=min_summary_count,
        skip_existing=skip_existing,
    )
    generated_advice = 0
    written_advice = 0
    failed_scopes = 0

    print(
        f"Fetched {len(scopes)} scopes. "
        f"limit={limit} min_summary_count={min_summary_count} "
        f"sample_size={sample_size} dry_run={dry_run} skip_existing={skip_existing}"
    )
    for index, scope in enumerate(scopes, 1):
        label = (
            f"{scope['primary_leaf_name']} / "
            f"{scope.get('product_tag_name') or '-'} / "
            f"{scope.get('request_tag_name') or '-'}"
        )
        try:
            samples = _fetch_scope_samples(scope, sample_size=sample_size)
            messages = _build_messages(scope, samples)
            raw_data = _call_model(messages)
            advices = _coerce_advices(raw_data)
            rows = _build_advice_rows(scope=scope, samples=samples, advices=advices)
            generated_advice += len(rows)
            if dry_run:
                print(f"[{index}/{len(scopes)}] DRY-RUN {label} generated={len(rows)}")
                print(json.dumps(rows, ensure_ascii=False, indent=2))
            else:
                written = _write_advice_rows(rows)
                written_advice += written
                print(f"[{index}/{len(scopes)}] OK {label} generated={len(rows)} written={written}")
        except Exception as exc:
            failed_scopes += 1
            print(f"[{index}/{len(scopes)}] ERROR {label} {type(exc).__name__}: {exc}")

    return BuilderSummary(
        scanned_scopes=len(scopes),
        generated_advice=generated_advice,
        written_advice=written_advice,
        failed_scopes=failed_scopes,
    )
