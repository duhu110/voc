from __future__ import annotations

import json
import time
import traceback
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from voc_agent.complaint_taxonomy_validator.chain import run_validator
from voc_agent.complaint_taxonomy_validator.tools import fetch_random_ticket_ids
from voc_agent.core.config import get_settings


OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def write_result_artifact(output_dir: Path, payload: dict[str, Any]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    ticket_id = payload.get("ticket_id", "unknown")
    timestamp = str(payload.get("timestamp", current_timestamp())).replace(":", "-")
    path = output_dir / f"{ticket_id}__{timestamp}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_summary_artifact(output_dir: Path, summary: dict[str, Any]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = str(summary.get("timestamp", current_timestamp())).replace(":", "-")
    path = output_dir / f"summary__{timestamp}.json"
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_markdown_report(output_dir: Path, summary: dict[str, Any]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = str(summary.get("timestamp", current_timestamp())).replace(":", "-")
    path = output_dir / f"report__{timestamp}.md"
    lines = [
        "# Complaint Taxonomy Validator Chain Batch Report",
        "",
        f"- 样本数 {summary['sample_size']}",
        f"- 成功 {summary['success_count']}",
        f"- 失败 {summary['failure_count']}",
        f"- 成功率 {summary['success_rate']:.0%}",
        "",
        "## 失败分布",
    ]
    failures_by_stage = summary.get("failures_by_stage", {})
    if failures_by_stage:
        for stage, count in failures_by_stage.items():
            lines.append(f"- {stage}: {count}")
    else:
        lines.append("- 无")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def current_timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def run_chain_batch_validation(sample_size: int = 20, output_dir: Path = OUTPUT_DIR) -> dict[str, Any]:
    settings = get_settings()
    ticket_ids = fetch_random_ticket_ids(limit=sample_size)
    if len(ticket_ids) != sample_size:
        raise RuntimeError(f"Expected {sample_size} random ticket IDs, got {len(ticket_ids)}")

    failures_by_stage: Counter[str] = Counter()
    result_files: list[str] = []
    summary: dict[str, Any] = {
        "timestamp": current_timestamp(),
        "sample_size": sample_size,
        "model_name": settings.llm_model_name,
        "ticket_ids": ticket_ids,
        "success_count": 0,
        "failure_count": 0,
        "success_rate": 0.0,
        "failures_by_stage": {},
        "results": [],
    }

    for ticket_id in ticket_ids:
        started_at = time.perf_counter()
        timestamp = current_timestamp()
        try:
            result = run_validator(ticket_id)
            duration_ms = int((time.perf_counter() - started_at) * 1000)
            payload = {
                "ticket_id": ticket_id,
                "status": "success",
                "stage": "chain",
                "duration_ms": duration_ms,
                "timestamp": timestamp,
                "model_name": settings.llm_model_name,
                "result": result,
            }
            summary["success_count"] += 1
        except Exception as exc:  # noqa: BLE001
            duration_ms = int((time.perf_counter() - started_at) * 1000)
            stage = classify_failure_stage(exc)
            failures_by_stage[stage] += 1
            payload = {
                "ticket_id": ticket_id,
                "status": "failed",
                "stage": stage,
                "duration_ms": duration_ms,
                "timestamp": timestamp,
                "model_name": settings.llm_model_name,
                "error_type": exc.__class__.__name__,
                "error_message": str(exc),
                "traceback": "".join(traceback.format_exception(exc)),
            }
            summary["failure_count"] += 1

        artifact_path = write_result_artifact(output_dir, payload)
        payload["artifact_path"] = str(artifact_path)
        result_files.append(str(artifact_path))
        summary["results"].append(payload)

    summary["success_rate"] = summary["success_count"] / sample_size if sample_size else 0.0
    summary["failures_by_stage"] = dict(failures_by_stage)
    summary["result_files"] = result_files

    summary_path = write_summary_artifact(output_dir, summary)
    summary["summary_path"] = str(summary_path)
    report_path = write_markdown_report(output_dir, summary)
    summary["report_path"] = str(report_path)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def classify_failure_stage(exc: Exception) -> str:
    if isinstance(exc, json.JSONDecodeError):
        return "parse"
    if isinstance(exc, ValidationError):
        return "schema"
    return "chain"
