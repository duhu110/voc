from __future__ import annotations

from typing import Any, TypedDict

from pydantic import BaseModel, Field


class KeywordCandidate(BaseModel):
    keyword: str = Field(description='提取出的关键词或短语')
    reason: str = Field(description='该关键词和投诉内容的关联理由')
    confidence: float = Field(ge=0.0, le=1.0, description='关键词判断置信度')


class CategoryCandidate(BaseModel):
    code: str = Field(description='分类编码')
    full_name: str = Field(description='分类完整名称')
    confidence: float = Field(ge=0.0, le=1.0, description='分类判断置信度')
    reason: str = Field(description='分类命中的简要依据')


class TagCandidate(BaseModel):
    group_code: str = Field(description='标签组编码')
    code: str = Field(description='标签编码')
    name: str = Field(description='标签名称')
    confidence: float = Field(ge=0.0, le=1.0, description='标签判断置信度')
    reason: str = Field(description='标签命中的简要依据')


class ValidatorOutput(BaseModel):
    summary: str = Field(description='对工单问题的简短总结')
    primary_category: CategoryCandidate = Field(description='最可能的主分类')
    candidate_categories: list[CategoryCandidate] = Field(default_factory=list, description='候选分类，包含主分类')
    candidate_tags: list[TagCandidate] = Field(default_factory=list, description='候选标签')
    category_keywords: list[KeywordCandidate] = Field(default_factory=list, description='有助于分类判断的关键词')
    tag_keywords: list[KeywordCandidate] = Field(default_factory=list, description='有助于标签判断的关键词')
    risks: list[str] = Field(default_factory=list, description='需要关注的风险或不确定点')


class ValidatorState(TypedDict, total=False):
    ticket_id: str
    ticket: dict[str, Any]
    categories: list[dict[str, Any]]
    tags: list[dict[str, Any]]
    result: dict[str, Any]
