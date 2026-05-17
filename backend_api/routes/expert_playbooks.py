from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from backend_api.db_utils import jsonable_row, pagination
from backend_api.schemas import ExpertPlaybookCreateRequest, ExpertPlaybookPatchRequest
from voc_agent.core.db import get_engine

router = APIRouter(prefix="/expert-playbooks", tags=["expert-playbooks"])

LIST_SQL = text(
    """
    select
      id, scenario_key, title, case_description, source_file, source_case_no,
      primary_leaf_code, primary_leaf_name, product_tag_code, product_tag_name,
      request_tag_code, request_tag_name, trigger_keywords, review_status,
      priority, status, created_at, updated_at
    from expert_handling_playbook
    where (cast(:status as varchar) is null or status = :status)
      and (cast(:review_status as varchar) is null or review_status = :review_status)
      and (cast(:primary_leaf_code as varchar) is null or primary_leaf_code = :primary_leaf_code)
      and (
        cast(:query as varchar) is null
        or title ilike :query_like
        or scenario_key ilike :query_like
        or case_description ilike :query_like
        or raw_case_text ilike :query_like
      )
    order by priority asc, updated_at desc, id desc
    limit :limit offset :offset
    """
)

COUNT_SQL = text(
    """
    select count(*) as total
    from expert_handling_playbook
    where (cast(:status as varchar) is null or status = :status)
      and (cast(:review_status as varchar) is null or review_status = :review_status)
      and (cast(:primary_leaf_code as varchar) is null or primary_leaf_code = :primary_leaf_code)
      and (
        cast(:query as varchar) is null
        or title ilike :query_like
        or scenario_key ilike :query_like
        or case_description ilike :query_like
        or raw_case_text ilike :query_like
      )
    """
)

DETAIL_SQL = text("select * from expert_handling_playbook where id = :id")


def _filters(
    *,
    query: str | None,
    status: str | None,
    review_status: str | None,
    primary_leaf_code: str | None,
    page: int,
    page_size: int,
) -> dict[str, Any]:
    limit, offset = pagination(page, page_size)
    query_clean = query.strip() if query else None
    return {
        "query": query_clean,
        "query_like": f"%{query_clean}%" if query_clean else None,
        "status": status,
        "review_status": review_status,
        "primary_leaf_code": primary_leaf_code,
        "limit": limit,
        "offset": offset,
    }


@router.get("")
async def list_expert_playbooks(
    query: str | None = None,
    status: str | None = None,
    review_status: str | None = None,
    primary_leaf_code: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    params = _filters(
        query=query,
        status=status,
        review_status=review_status,
        primary_leaf_code=primary_leaf_code,
        page=page,
        page_size=page_size,
    )
    with get_engine().connect() as conn:
        rows = conn.execute(LIST_SQL, params).mappings().all()
        total = conn.execute(COUNT_SQL, params).scalar_one()
    return {
        "status": "success",
        "items": [jsonable_row(row) for row in rows],
        "total": total,
        "page": page,
        "page_size": params["limit"],
    }


@router.get("/{playbook_id}")
async def get_expert_playbook(playbook_id: int) -> dict:
    with get_engine().connect() as conn:
        row = conn.execute(DETAIL_SQL, {"id": playbook_id}).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail="Expert playbook not found")
    return {"status": "success", "item": jsonable_row(row)}


@router.post("")
async def create_expert_playbook(request: ExpertPlaybookCreateRequest) -> dict:
    sql = text(
        """
        insert into expert_handling_playbook (
          scenario_key, title, case_description, source_file, source_case_no, source_case_title,
          trigger_keywords, primary_leaf_code, primary_leaf_name, product_tag_code, product_tag_name,
          request_tag_code, request_tag_name, verify_steps, judgment_rules, execution_steps,
          callback_requirements, communication_tips, raw_case_text, review_status, priority, status
        )
        values (
          :scenario_key, :title, :case_description, :source_file, :source_case_no, :source_case_title,
          cast(:trigger_keywords as jsonb), :primary_leaf_code, :primary_leaf_name, :product_tag_code, :product_tag_name,
          :request_tag_code, :request_tag_name, cast(:verify_steps as jsonb), cast(:judgment_rules as jsonb),
          cast(:execution_steps as jsonb), cast(:callback_requirements as jsonb), cast(:communication_tips as jsonb),
          :raw_case_text, :review_status, :priority, :status
        )
        returning *
        """
    )
    payload = request.model_dump()
    for key in (
        "trigger_keywords",
        "verify_steps",
        "judgment_rules",
        "execution_steps",
        "callback_requirements",
        "communication_tips",
    ):
        payload[key] = json.dumps(payload[key], ensure_ascii=False)
    with get_engine().begin() as conn:
        row = conn.execute(sql, payload).mappings().one()
    return {"status": "success", "item": jsonable_row(row)}


@router.patch("/{playbook_id}")
async def patch_expert_playbook(playbook_id: int, request: ExpertPlaybookPatchRequest) -> dict:
    allowed = request.model_dump(exclude_unset=True)
    if not allowed:
        return await get_expert_playbook(playbook_id)
    json_fields = {
        "trigger_keywords",
        "verify_steps",
        "judgment_rules",
        "execution_steps",
        "callback_requirements",
        "communication_tips",
    }
    set_clauses: list[str] = []
    params: dict[str, Any] = {"id": playbook_id}
    for key, value in allowed.items():
        params[key] = json.dumps(value, ensure_ascii=False) if key in json_fields else value
        if key in json_fields:
            set_clauses.append(f"{key} = cast(:{key} as jsonb)")
        else:
            set_clauses.append(f"{key} = :{key}")
    set_clauses.append("updated_at = current_timestamp")
    sql = text(
        f"""
        update expert_handling_playbook
        set {", ".join(set_clauses)}
        where id = :id
        returning *
        """
    )
    with get_engine().begin() as conn:
        row = conn.execute(sql, params).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail="Expert playbook not found")
    return {"status": "success", "item": jsonable_row(row)}
