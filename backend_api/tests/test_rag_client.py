from __future__ import annotations

import json

import httpx
import pytest

from backend_api.rag_client import RagClient, RagServiceError


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_rag_client_search_posts_to_kb_search_endpoint() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/knowledge-bases/kb-1/search"
        assert json.loads(request.content) == {"query": "用户投诉乱扣费", "top_k": 2}
        return httpx.Response(
            200,
            json={"status": "success", "results": [{"chunk_id": 1, "content": "处理步骤"}]},
        )

    client = RagClient(
        base_url="http://rag.test",
        timeout=1,
        transport=httpx.MockTransport(handler),
    )

    result = await client.search(kb_id="kb-1", query="用户投诉乱扣费", top_k=2)

    assert result["status"] == "success"
    assert result["results"][0]["content"] == "处理步骤"


@pytest.mark.anyio
async def test_rag_client_raises_for_service_error() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="boom")

    client = RagClient(
        base_url="http://rag.test",
        timeout=1,
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(RagServiceError, match="500"):
        await client.health()
