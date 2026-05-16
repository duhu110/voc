#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from sqlalchemy import text


def find_repo_root() -> Path:
    current = Path(__file__).resolve()
    for path in [current.parent, *current.parents]:
        if (path / "pyproject.toml").exists() and (path / "voc_agent").exists():
            return path
    raise RuntimeError("Could not find project root containing pyproject.toml and voc_agent")


REPO_ROOT = find_repo_root()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend_api.rag_client import RagClient  # noqa: E402
from voc_agent.core.db import get_engine  # noqa: E402


KNOWLEDGE_BASES = [
    {
        "logical_name": "voc-expert-playbooks",
        "display_name": "VOC 专家经验库",
        "description": "专家处理案例和可执行处理剧本",
        "metadata": {"owner": "voc", "source": "expert_handling_playbook"},
    },
    {
        "logical_name": "voc-handling-advices",
        "display_name": "VOC 历史建议库",
        "description": "从历史处理摘要归纳出的可复用处理建议",
        "metadata": {"owner": "voc", "source": "converger_handling_advice"},
    },
    {
        "logical_name": "voc-resolution-summaries",
        "display_name": "VOC 历史处理摘要库",
        "description": "高质量历史处理摘要和相似处理路径",
        "metadata": {"owner": "voc", "source": "converger_resolution_summary_atomic"},
    },
    {
        "logical_name": "voc-policy-docs",
        "display_name": "VOC 政策规则与回单规范库",
        "description": "政策、规则、业务口径、回单规范等文档",
        "metadata": {"owner": "voc", "source": "policy_docs"},
    },
]

UPSERT_SQL = text(
    """
    insert into rag_knowledge_bases (
        logical_name,
        rag_kb_id,
        display_name,
        description,
        metadata,
        status,
        updated_at
    )
    values (
        :logical_name,
        cast(:rag_kb_id as uuid),
        :display_name,
        :description,
        cast(:metadata as jsonb),
        'active',
        now()
    )
    on conflict (logical_name) do update
    set rag_kb_id = excluded.rag_kb_id,
        display_name = excluded.display_name,
        description = excluded.description,
        metadata = excluded.metadata,
        status = 'active',
        updated_at = now()
    """
)


def _items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    items = payload.get("items") or payload.get("knowledge_bases") or []
    return [item for item in items if isinstance(item, dict)]


async def ensure_rag_knowledge_bases() -> list[dict[str, Any]]:
    client = RagClient()
    existing = {
        item.get("name"): item
        for item in _items(await client.list_knowledge_bases())
        if item.get("name")
    }
    ensured: list[dict[str, Any]] = []
    for spec in KNOWLEDGE_BASES:
        logical_name = spec["logical_name"]
        item = existing.get(logical_name)
        if item is None:
            created = await client.create_knowledge_base(
                name=logical_name,
                description=spec["description"],
                metadata=spec["metadata"],
            )
            item = created.get("knowledge_base") or {}
        ensured.append({**spec, "rag_kb_id": item["kb_id"]})
    return ensured


def upsert_mappings(rows: list[dict[str, Any]]) -> None:
    with get_engine().begin() as conn:
        for row in rows:
            conn.execute(
                UPSERT_SQL,
                {
                    "logical_name": row["logical_name"],
                    "rag_kb_id": row["rag_kb_id"],
                    "display_name": row["display_name"],
                    "description": row["description"],
                    "metadata": json.dumps(row["metadata"], ensure_ascii=False),
                },
            )


def main() -> int:
    rows = asyncio.run(ensure_rag_knowledge_bases())
    upsert_mappings(rows)
    for row in rows:
        print(f"{row['logical_name']} -> {row['rag_kb_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
