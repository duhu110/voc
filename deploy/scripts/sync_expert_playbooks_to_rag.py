#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import sys
import time
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


PLAYBOOK_SQL = text(
    """
    select *
    from expert_handling_playbook
    where status = 'active'
      and review_status = 'reviewed'
    order by priority asc, id asc
    """
)

KB_SQL = text(
    """
    select id, logical_name, rag_kb_id::text as rag_kb_id
    from rag_knowledge_bases
    where logical_name = 'voc-expert-playbooks'
      and status = 'active'
    """
)

EXISTING_DOC_SQL = text(
    """
    select id, rag_document_id::text as rag_document_id, rag_task_id::text as rag_task_id, task_status
    from rag_documents
    where source_table = 'expert_handling_playbook'
      and source_id = :source_id
      and source_version = :source_version
      and status = 'active'
    limit 1
    """
)

UPSERT_DOCUMENT_SQL = text(
    """
    insert into rag_documents (
        knowledge_base_id,
        rag_document_id,
        rag_task_id,
        external_id,
        source_table,
        source_id,
        source_version,
        content_hash,
        title,
        metadata,
        task_status,
        status,
        updated_at
    )
    values (
        :knowledge_base_id,
        cast(:rag_document_id as uuid),
        cast(:rag_task_id as uuid),
        :external_id,
        'expert_handling_playbook',
        :source_id,
        :source_version,
        :content_hash,
        :title,
        cast(:metadata as jsonb),
        :task_status,
        'active',
        now()
    )
    on conflict (knowledge_base_id, external_id) do update
    set rag_document_id = excluded.rag_document_id,
        rag_task_id = excluded.rag_task_id,
        content_hash = excluded.content_hash,
        title = excluded.title,
        metadata = excluded.metadata,
        task_status = excluded.task_status,
        status = 'active',
        updated_at = now()
    """
)

UPSERT_TASK_SQL = text(
    """
    insert into rag_ingestion_tasks (
        rag_task_id,
        rag_document_id,
        rag_kb_id,
        source_table,
        source_id,
        task_status,
        progress_current,
        progress_total,
        error_message,
        raw_task,
        updated_at,
        completed_at
    )
    values (
        cast(:rag_task_id as uuid),
        cast(:rag_document_id as uuid),
        cast(:rag_kb_id as uuid),
        'expert_handling_playbook',
        cast(:source_id as varchar),
        cast(:task_status as varchar),
        :progress_current,
        :progress_total,
        :error_message,
        cast(:raw_task as jsonb),
        now(),
        case when cast(:task_status as varchar) = 'completed' then now() else null end
    )
    on conflict (rag_task_id) do update
    set task_status = excluded.task_status,
        progress_current = excluded.progress_current,
        progress_total = excluded.progress_total,
        error_message = excluded.error_message,
        raw_task = excluded.raw_task,
        updated_at = now(),
        completed_at = case when excluded.task_status = 'completed' then now() else rag_ingestion_tasks.completed_at end
    """
)

UPDATE_DOCUMENT_STATUS_SQL = text(
    """
    update rag_documents
    set task_status = :task_status,
        updated_at = now()
    where rag_task_id = cast(:rag_task_id as uuid)
    """
)


def _json_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return [value]
        return parsed if isinstance(parsed, list) else [parsed]
    return [value]


def _section(title: str, items: list[Any]) -> str:
    clean_items = [str(item).strip() for item in items if str(item).strip()]
    if not clean_items:
        return ""
    lines = [f"## {title}", ""]
    lines.extend(f"{index}. {item}" for index, item in enumerate(clean_items, start=1))
    return "\n".join(lines)


def render_playbook_markdown(row: dict[str, Any]) -> str:
    title = str(row.get("title") or f"专家经验 {row['id']}").strip()
    parts = [
        f"# {title}",
        "",
        f"- 专家经验ID：{row['id']}",
        f"- 场景键：{row.get('scenario_key') or ''}",
        f"- 分类：{row.get('primary_leaf_name') or row.get('primary_leaf_code') or ''}",
        f"- 产品标签：{row.get('product_tag_name') or row.get('product_tag_code') or ''}",
        f"- 诉求标签：{row.get('request_tag_name') or row.get('request_tag_code') or ''}",
        f"- 来源：{row.get('source_file') or ''} / {row.get('source_case_no') or ''} / {row.get('source_case_title') or ''}",
        "",
    ]
    if row.get("case_description"):
        parts.extend(["## 案例说明", "", str(row["case_description"]).strip(), ""])
    keywords = _json_list(row.get("trigger_keywords"))
    if keywords:
        parts.extend(["## 触发关键词", "", "、".join(str(item) for item in keywords), ""])
    for heading, key in [
        ("先核实事实", "verify_steps"),
        ("判断规则和责任", "judgment_rules"),
        ("执行处理动作", "execution_steps"),
        ("回访和回单要求", "callback_requirements"),
        ("沟通技巧", "communication_tips"),
    ]:
        section = _section(heading, _json_list(row.get(key)))
        if section:
            parts.extend([section, ""])
    if row.get("raw_case_text"):
        parts.extend(["## 原始案例全文", "", str(row["raw_case_text"]).strip(), ""])
    return "\n".join(parts).strip() + "\n"


def fetch_kb_and_playbooks() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    with get_engine().connect() as conn:
        kb = conn.execute(KB_SQL).mappings().first()
        if kb is None:
            raise RuntimeError("Missing active rag_knowledge_bases mapping for voc-expert-playbooks")
        rows = conn.execute(PLAYBOOK_SQL).mappings().all()
    return dict(kb), [dict(row) for row in rows]


def record_upload(
    *,
    kb: dict[str, Any],
    row: dict[str, Any],
    external_id: str,
    source_version: str,
    content_hash: str,
    metadata: dict[str, Any],
    upload_result: dict[str, Any],
) -> None:
    task_id = upload_result["task_id"]
    document_id = upload_result["document_id"]
    task_status = upload_result.get("task_status") or "queued"
    with get_engine().begin() as conn:
        conn.execute(
            UPSERT_DOCUMENT_SQL,
            {
                "knowledge_base_id": kb["id"],
                "rag_document_id": document_id,
                "rag_task_id": task_id,
                "external_id": external_id,
                "source_id": str(row["id"]),
                "source_version": source_version,
                "content_hash": content_hash,
                "title": row.get("title"),
                "metadata": json.dumps(metadata, ensure_ascii=False),
                "task_status": task_status,
            },
        )
        conn.execute(
            UPSERT_TASK_SQL,
            {
                "rag_task_id": task_id,
                "rag_document_id": document_id,
                "rag_kb_id": kb["rag_kb_id"],
                "source_id": str(row["id"]),
                "task_status": task_status,
                "progress_current": 0,
                "progress_total": 4,
                "error_message": None,
                "raw_task": json.dumps(upload_result, ensure_ascii=False),
            },
        )


def record_task_status(task_id: str, task: dict[str, Any]) -> None:
    task_status = task.get("status") or "unknown"
    with get_engine().begin() as conn:
        conn.execute(
            UPSERT_TASK_SQL,
            {
                "rag_task_id": task_id,
                "rag_document_id": task.get("document_id"),
                "rag_kb_id": task.get("knowledge_base_id"),
                "source_id": None,
                "task_status": task_status,
                "progress_current": int(task.get("progress_current") or 0),
                "progress_total": int(task.get("progress_total") or 4),
                "error_message": task.get("error_message"),
                "raw_task": json.dumps(task, ensure_ascii=False),
            },
        )
        conn.execute(UPDATE_DOCUMENT_STATUS_SQL, {"rag_task_id": task_id, "task_status": task_status})


def already_synced(source_id: str, source_version: str) -> bool:
    with get_engine().connect() as conn:
        existing = conn.execute(
            EXISTING_DOC_SQL,
            {"source_id": source_id, "source_version": source_version},
        ).mappings().first()
    return existing is not None


async def wait_for_tasks(task_ids: list[str], *, timeout_seconds: int, poll_seconds: float) -> dict[str, int]:
    client = RagClient()
    deadline = time.monotonic() + timeout_seconds
    remaining = set(task_ids)
    counts = {"completed": 0, "failed": 0, "timeout": 0}
    while remaining and time.monotonic() < deadline:
        for task_id in list(remaining):
            payload = await client.get_task(task_id)
            task = payload.get("task") or {}
            record_task_status(task_id, task)
            status = task.get("status")
            if status == "completed":
                counts["completed"] += 1
                remaining.remove(task_id)
            elif status == "failed":
                counts["failed"] += 1
                remaining.remove(task_id)
        if remaining:
            await asyncio.sleep(poll_seconds)
    if remaining:
        counts["timeout"] = len(remaining)
    return counts


async def sync_playbooks(*, limit: int | None, wait: bool, force: bool) -> dict[str, int]:
    kb, rows = fetch_kb_and_playbooks()
    if limit:
        rows = rows[:limit]
    client = RagClient()
    uploaded_task_ids: list[str] = []
    counts = {"selected": len(rows), "uploaded": 0, "skipped": 0}
    for row in rows:
        markdown = render_playbook_markdown(row)
        content = markdown.encode("utf-8")
        content_hash = hashlib.sha256(content).hexdigest()
        source_version = f"sha256:{content_hash[:16]}"
        source_id = str(row["id"])
        if not force and already_synced(source_id, source_version):
            counts["skipped"] += 1
            continue
        external_id = f"expert_handling_playbook:{source_id}:{content_hash[:16]}"
        metadata = {
            "source_table": "expert_handling_playbook",
            "source_id": source_id,
            "source_version": source_version,
            "scenario_key": row.get("scenario_key"),
            "primary_leaf_code": row.get("primary_leaf_code"),
            "primary_leaf_name": row.get("primary_leaf_name"),
            "review_status": row.get("review_status"),
            "status": row.get("status"),
        }
        upload_result = await client.upload_document_bytes(
            kb_id=kb["rag_kb_id"],
            filename=f"expert_playbook_{source_id}.md",
            content=content,
            content_type="text/markdown; charset=utf-8",
            external_id=external_id,
            title=row.get("title") or f"专家经验 {source_id}",
            metadata=metadata,
        )
        record_upload(
            kb=kb,
            row=row,
            external_id=external_id,
            source_version=source_version,
            content_hash=content_hash,
            metadata=metadata,
            upload_result=upload_result,
        )
        uploaded_task_ids.append(upload_result["task_id"])
        counts["uploaded"] += 1
        print(f"uploaded expert_handling_playbook:{source_id} task={upload_result['task_id']}")
    if wait and uploaded_task_ids:
        wait_counts = await wait_for_tasks(uploaded_task_ids, timeout_seconds=600, poll_seconds=2)
        counts.update({f"tasks_{key}": value for key, value in wait_counts.items()})
    return counts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sync expert_handling_playbook rows into the voc-expert-playbooks RAG knowledge base.")
    parser.add_argument("--limit", type=int, default=None, help="Only sync the first N playbooks.")
    parser.add_argument("--no-wait", action="store_true", help="Do not wait for RAG ingestion tasks to finish.")
    parser.add_argument("--force", action="store_true", help="Upload even if the same content hash was already synced.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    counts = asyncio.run(sync_playbooks(limit=args.limit, wait=not args.no_wait, force=args.force))
    print(json.dumps(counts, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
