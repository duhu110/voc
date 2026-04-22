from __future__ import annotations

from typing import Any, TypedDict

from pydantic import BaseModel, Field


class PrimaryCategorySelection(BaseModel):
    level1_code: str = Field(description="一级分类编码")
    level1_name: str = Field(description="一级分类名称")
    level2_code: str = Field(description="二级分类编码")
    level2_name: str = Field(description="二级分类名称")
    leaf_code: str = Field(description="叶子分类编码")
    leaf_name: str = Field(description="叶子分类名称")
    reason: str = Field(description="分类理由")


class PrimaryCategoryNodeOutput(BaseModel):
    summary: str = Field(description="对工单分类结果的简短概括")
    primary_category: PrimaryCategorySelection = Field(description="主分类结果")


class ControlledTagSelection(BaseModel):
    code: str = Field(description="标签编码")
    name: str = Field(description="标签名称")
    reason: str = Field(description="选择理由")


class LineCategorySelection(BaseModel):
    value: str = Field(description="原始工单中的 line_category")
    reason: str = Field(description="固定说明，表示该值直接来自原始工单")


class ControlledTagsNodeOutput(BaseModel):
    request_tag: ControlledTagSelection
    emotion_tag: ControlledTagSelection
    risk_tag: ControlledTagSelection
    product_tag: ControlledTagSelection
    line_category: LineCategorySelection


class ResolutionSummaryNodeOutput(BaseModel):
    resolution_summary: str | None = None


class ConvergerState(TypedDict, total=False):
    ticket_id: str
    ticket: dict[str, Any]
    runtime_data: dict[str, Any]
    result: dict[str, Any]
    category_summary: str
    primary_category: dict[str, Any]
    status: str
    stop_reason: str
    category_prompt: str
    category_raw_response: str
    tags_prompt: str
    tags_raw_response: str
    request_tag: dict[str, Any]
    emotion_tag: dict[str, Any]
    risk_tag: dict[str, Any]
    product_tag: dict[str, Any]
    line_category: dict[str, Any]
    resolution_summary: str | None
