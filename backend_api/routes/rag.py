from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from sqlalchemy import text

from backend_api.db_utils import jsonable_row
from backend_api.rag_client import RagClient, RagServiceError
from backend_api.schemas import KnowledgeBaseCreateRequest, RagSearchRequest
from voc_agent.core.db import get_engine

router = APIRouter(prefix="/rag", tags=["rag"])


def _rag_error(exc: RagServiceError) -> HTTPException:
    return HTTPException(status_code=502, detail=str(exc))


@router.get("/health")
async def rag_health() -> dict:
    try:
        return await RagClient().health()
    except RagServiceError as exc:
        raise _rag_error(exc) from exc


@router.post("/knowledge-bases")
async def create_knowledge_base(request: KnowledgeBaseCreateRequest) -> dict:
    try:
        return await RagClient().create_knowledge_base(
            name=request.name,
            description=request.description,
            metadata=request.metadata,
        )
    except RagServiceError as exc:
        raise _rag_error(exc) from exc


@router.get("/knowledge-bases")
async def list_knowledge_bases() -> dict:
    try:
        return await RagClient().list_knowledge_bases()
    except RagServiceError as exc:
        raise _rag_error(exc) from exc


@router.get("/mappings")
async def list_local_knowledge_base_mappings() -> dict:
    sql = text(
        """
        select
          kb.id, kb.logical_name, kb.rag_kb_id::text as rag_kb_id, kb.display_name,
          kb.description, kb.metadata, kb.status, kb.created_at, kb.updated_at,
          count(doc.id) filter (where doc.status = 'active') as active_document_count,
          count(doc.id) as total_document_count
        from rag_knowledge_bases kb
        left join rag_documents doc on doc.knowledge_base_id = kb.id
        group by kb.id
        order by kb.logical_name
        """
    )
    with get_engine().connect() as conn:
        rows = conn.execute(sql).mappings().all()
    return {"status": "success", "items": [jsonable_row(row) for row in rows]}


@router.get("/documents")
async def list_local_rag_documents(
    logical_name: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> dict:
    filters = []
    params: dict[str, object] = {"limit": limit}
    if logical_name:
        filters.append("kb.logical_name = :logical_name")
        params["logical_name"] = logical_name

    where_clause = f"where {' and '.join(filters)}" if filters else ""
    sql = text(
        f"""
        select
          doc.id,
          kb.logical_name,
          kb.display_name as knowledge_base_name,
          kb.rag_kb_id::text as rag_kb_id,
          doc.rag_document_id::text as rag_document_id,
          doc.rag_task_id::text as rag_task_id,
          doc.external_id,
          doc.source_table,
          doc.source_id,
          doc.source_version,
          doc.title,
          doc.metadata,
          doc.task_status,
          doc.status,
          doc.created_at,
          doc.updated_at
        from rag_documents doc
        join rag_knowledge_bases kb on kb.id = doc.knowledge_base_id
        {where_clause}
        order by doc.updated_at desc, doc.id desc
        limit :limit
        """
    )
    with get_engine().connect() as conn:
        rows = conn.execute(sql, params).mappings().all()
    return {"status": "success", "items": [jsonable_row(row) for row in rows]}


@router.get("/tasks")
async def list_local_rag_tasks(
    status: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> dict:
    filters = []
    params: dict[str, object] = {"limit": limit}
    if status:
        filters.append("task_status = :status")
        params["status"] = status

    where_clause = f"where {' and '.join(filters)}" if filters else ""
    sql = text(
        f"""
        select
          id,
          rag_task_id::text as rag_task_id,
          rag_document_id::text as rag_document_id,
          rag_kb_id::text as rag_kb_id,
          source_table,
          source_id,
          task_status,
          progress_current,
          progress_total,
          error_message,
          raw_task,
          created_at,
          updated_at,
          completed_at
        from rag_ingestion_tasks
        {where_clause}
        order by updated_at desc, id desc
        limit :limit
        """
    )
    with get_engine().connect() as conn:
        rows = conn.execute(sql, params).mappings().all()
    return {"status": "success", "items": [jsonable_row(row) for row in rows]}


@router.get("/knowledge-bases/{kb_id}")
async def get_knowledge_base(kb_id: str) -> dict:
    try:
        return await RagClient().get_knowledge_base(kb_id)
    except RagServiceError as exc:
        raise _rag_error(exc) from exc


@router.delete("/knowledge-bases/{kb_id}")
async def delete_knowledge_base(kb_id: str) -> dict:
    try:
        return await RagClient().delete_knowledge_base(kb_id)
    except RagServiceError as exc:
        raise _rag_error(exc) from exc


@router.post("/knowledge-bases/{kb_id}/documents")
async def upload_document(
    kb_id: str,
    file: Annotated[UploadFile, File()],
    external_id: Annotated[str | None, Form()] = None,
    title: Annotated[str | None, Form()] = None,
    metadata_json: Annotated[str | None, Form()] = None,
) -> dict:
    metadata = {}
    if metadata_json:
        try:
            parsed = json.loads(metadata_json)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=422, detail="metadata_json must be valid JSON") from exc
        if not isinstance(parsed, dict):
            raise HTTPException(status_code=422, detail="metadata_json must be a JSON object")
        metadata = parsed
    try:
        return await RagClient().upload_document(
            kb_id=kb_id,
            file=file,
            external_id=external_id,
            title=title,
            metadata=metadata,
        )
    except RagServiceError as exc:
        raise _rag_error(exc) from exc


@router.get("/tasks/{task_id}")
async def get_task(task_id: str) -> dict:
    try:
        return await RagClient().get_task(task_id)
    except RagServiceError as exc:
        raise _rag_error(exc) from exc


@router.post("/tasks/{task_id}/retry")
async def retry_task(task_id: str) -> dict:
    try:
        return await RagClient().retry_task(task_id)
    except RagServiceError as exc:
        raise _rag_error(exc) from exc


@router.post("/knowledge-bases/{kb_id}/search")
async def search_knowledge_base(kb_id: str, request: RagSearchRequest) -> dict:
    try:
        return await RagClient().search(kb_id=kb_id, query=request.query, top_k=request.top_k)
    except RagServiceError as exc:
        raise _rag_error(exc) from exc


@router.post("/mappings/{logical_name}/search")
async def search_by_logical_name(logical_name: str, request: RagSearchRequest) -> dict:
    with get_engine().connect() as conn:
        row = conn.execute(
            text(
                """
                select logical_name, rag_kb_id::text as rag_kb_id
                from rag_knowledge_bases
                where logical_name = :logical_name
                  and status = 'active'
                """
            ),
            {"logical_name": logical_name},
        ).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail="RAG knowledge base mapping not found")
    try:
        result = await RagClient().search(kb_id=row["rag_kb_id"], query=request.query, top_k=request.top_k)
    except RagServiceError as exc:
        raise _rag_error(exc) from exc
    with get_engine().begin() as conn:
        conn.execute(
            text(
                """
                insert into rag_retrieval_logs (
                    knowledge_base_logical_name,
                    rag_kb_id,
                    query,
                    top_k,
                    result_count,
                    results
                )
                values (
                    :logical_name,
                    cast(:rag_kb_id as uuid),
                    :query,
                    :top_k,
                    :result_count,
                    cast(:results as jsonb)
                )
                """
            ),
            {
                "logical_name": logical_name,
                "rag_kb_id": row["rag_kb_id"],
                "query": request.query,
                "top_k": request.top_k,
                "result_count": len(result.get("results") or []),
                "results": json.dumps(result.get("results") or [], ensure_ascii=False),
            },
        )
    return result
