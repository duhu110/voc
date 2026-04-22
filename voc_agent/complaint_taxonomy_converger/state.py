from __future__ import annotations

from typing import Any, Literal, TypedDict

from pydantic import BaseModel, Field


class SelectedCategory(BaseModel):
    code: str
    full_name: str
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str


class SelectedTag(BaseModel):
    group_code: str
    code: str
    name: str
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str


class ConvergerResult(BaseModel):
    ticket_id: str
    status: Literal['completed', 'skipped_no_category']
    summary: str
    primary_category: SelectedCategory | None = None
    selected_tags: list[SelectedTag] = Field(default_factory=list)
    stop_reason: str | None = None


class ConvergerState(TypedDict, total=False):
    ticket_id: str
    ticket: dict[str, Any]
    categories: list[dict[str, Any]]
    tags: list[dict[str, Any]]
    category_summary: str
    selected_category: dict[str, Any] | None
    selected_tags: list[dict[str, Any]]
    stop_reason: str | None
    result: dict[str, Any]
