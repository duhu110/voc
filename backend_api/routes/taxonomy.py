from __future__ import annotations

import json

from fastapi import APIRouter

from voc_agent.core.config import get_settings

router = APIRouter(prefix="/taxonomy", tags=["taxonomy"])


def _load_json(name: str) -> dict:
    path = get_settings().repo_root / "voc_agent" / "converger_agent" / "data" / name
    return json.loads(path.read_text(encoding="utf-8"))


@router.get("/categories")
async def get_categories() -> dict:
    return {"status": "success", "data": _load_json("category_v2.json")}


@router.get("/tags/{tag_group}")
async def get_tags(tag_group: str) -> dict:
    file_map = {
        "request": "request_tags.json",
        "emotion": "emotion_tags.json",
        "risk": "risk_tags.json",
        "product": "product_tags.json",
    }
    if tag_group not in file_map:
        return {"status": "error", "message": "unknown tag group", "allowed": sorted(file_map)}
    return {"status": "success", "data": _load_json(file_map[tag_group])}

