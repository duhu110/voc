from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

import httpx
from fastapi import UploadFile

from voc_agent.core.config import get_settings


class RagServiceError(RuntimeError):
    """Raised when the external RAG service returns an error response."""


class RagClient:
    def __init__(
        self,
        *,
        base_url: str | None = None,
        timeout: float | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.rag_base_url).rstrip("/")
        self.timeout = timeout if timeout is not None else settings.rag_timeout_seconds
        self._transport = transport

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            transport=self._transport,
        ) as client:
            response = await client.request(method, path, **kwargs)
        if response.status_code >= 400:
            raise RagServiceError(f"RAG service returned {response.status_code}: {response.text[:500]}")
        payload = response.json()
        if not isinstance(payload, dict):
            raise RagServiceError("RAG service returned a non-object JSON payload")
        return payload

    async def health(self) -> dict[str, Any]:
        return await self._request("GET", "/health")

    async def create_knowledge_base(
        self,
        *,
        name: str,
        description: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            "/knowledge-bases",
            json={
                "name": name,
                "description": description,
                "metadata": dict(metadata or {}),
            },
        )

    async def list_knowledge_bases(self) -> dict[str, Any]:
        return await self._request("GET", "/knowledge-bases")

    async def get_knowledge_base(self, kb_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/knowledge-bases/{kb_id}")

    async def delete_knowledge_base(self, kb_id: str) -> dict[str, Any]:
        return await self._request("DELETE", f"/knowledge-bases/{kb_id}")

    async def upload_document(
        self,
        *,
        kb_id: str,
        file: UploadFile,
        external_id: str | None = None,
        title: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        content = await file.read()
        data: dict[str, str] = {}
        if external_id:
            data["external_id"] = external_id
        if title:
            data["title"] = title
        if metadata:
            data["metadata_json"] = json.dumps(dict(metadata), ensure_ascii=False)
        files = {
            "file": (
                file.filename or "upload.bin",
                content,
                file.content_type or "application/octet-stream",
            )
        }
        return await self._request(
            "POST",
            f"/knowledge-bases/{kb_id}/documents",
            data=data,
            files=files,
        )

    async def upload_document_bytes(
        self,
        *,
        kb_id: str,
        filename: str,
        content: bytes,
        content_type: str = "text/markdown",
        external_id: str | None = None,
        title: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        data: dict[str, str] = {}
        if external_id:
            data["external_id"] = external_id
        if title:
            data["title"] = title
        if metadata:
            data["metadata_json"] = json.dumps(dict(metadata), ensure_ascii=False)
        files = {"file": (filename, content, content_type)}
        return await self._request(
            "POST",
            f"/knowledge-bases/{kb_id}/documents",
            data=data,
            files=files,
        )

    async def get_task(self, task_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/tasks/{task_id}")

    async def retry_task(self, task_id: str) -> dict[str, Any]:
        return await self._request("POST", f"/tasks/{task_id}/retry")

    async def search(self, *, kb_id: str, query: str, top_k: int = 3) -> dict[str, Any]:
        return await self._request(
            "POST",
            f"/knowledge-bases/{kb_id}/search",
            json={"query": query, "top_k": top_k},
        )
