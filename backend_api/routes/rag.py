from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend_api.rag_client import RagClient, RagServiceError
from backend_api.schemas import KnowledgeBaseCreateRequest, RagSearchRequest

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

