from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "voc_agent" / "converger_agent" / "data"


def _read_json(file_name: str) -> dict[str, Any]:
    path = DATA_DIR / file_name
    return json.loads(path.read_text(encoding="utf-8"))


def load_manifest() -> dict[str, Any]:
    return _read_json("manifest.json")


def build_persistence_rows(
    *,
    result: dict[str, Any],
    model_name: str,
    taxonomy_version: str,
    agent_version: str,
) -> dict[str, dict[str, Any] | None]:
    if result.get("status") != "completed":
        return {
            "result_row": None,
            "resolution_summary_row": None,
        }

    primary_category = result["primary_category"]
    request_tag = result["request_tag"]
    emotion_tag = result["emotion_tag"]
    risk_tag = result["risk_tag"]
    product_tag = result["product_tag"]
    line_category = result["line_category"]

    result_row = {
        "ticket_id": result["ticket_id"],
        "primary_level1_code": primary_category["level1_code"],
        "primary_level1_name": primary_category["level1_name"],
        "primary_level2_code": primary_category["level2_code"],
        "primary_level2_name": primary_category["level2_name"],
        "primary_leaf_code": primary_category["leaf_code"],
        "primary_leaf_name": primary_category["leaf_name"],
        "request_tag_code": request_tag["code"],
        "request_tag_name": request_tag["name"],
        "emotion_tag_code": emotion_tag["code"],
        "emotion_tag_name": emotion_tag["name"],
        "risk_tag_code": risk_tag["code"],
        "risk_tag_name": risk_tag["name"],
        "product_tag_code": product_tag["code"],
        "product_tag_name": product_tag["name"],
        "line_category": line_category["value"],
        "model_name": model_name,
        "taxonomy_version": taxonomy_version,
        "agent_version": agent_version,
        "status": result["status"],
    }

    resolution_summary = result.get("resolution_summary")
    resolution_summary_row = None
    if resolution_summary:
        resolution_summary_row = {
            "source_ticket_id": result["ticket_id"],
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
            "line_category": line_category["value"],
            "resolution_summary": resolution_summary,
            "model_name": model_name,
            "taxonomy_version": taxonomy_version,
            "agent_version": agent_version,
            "status": "active",
        }

    return {
        "result_row": result_row,
        "resolution_summary_row": resolution_summary_row,
    }
