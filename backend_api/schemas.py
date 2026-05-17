from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AdviceRequest(BaseModel):
    ticket_id: str | None = None
    ticket_payload: dict[str, Any] | None = None
    use_existing_classification: bool = False
    include_processing_context: bool = False
    advice_limit: int = Field(default=5, ge=1, le=20)
    sample_limit: int = Field(default=5, ge=0, le=20)

    @model_validator(mode="after")
    def require_one_ticket_source(self) -> "AdviceRequest":
        if bool(self.ticket_id) == bool(self.ticket_payload):
            raise ValueError("Provide exactly one of ticket_id or ticket_payload")
        return self


class KnowledgeBaseCreateRequest(BaseModel):
    name: str
    description: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RagSearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=3, ge=1, le=20)


class RagDocumentMetadata(BaseModel):
    model_config = ConfigDict(extra="allow")


class ExpertPlaybookCreateRequest(BaseModel):
    scenario_key: str
    title: str
    case_description: str | None = None
    source_file: str = "manual"
    source_case_no: int | None = None
    source_case_title: str | None = None
    trigger_keywords: list[str] = Field(default_factory=list)
    primary_leaf_code: str | None = None
    primary_leaf_name: str | None = None
    product_tag_code: str | None = None
    product_tag_name: str | None = None
    request_tag_code: str | None = None
    request_tag_name: str | None = None
    verify_steps: list[str] = Field(default_factory=list)
    judgment_rules: list[str] = Field(default_factory=list)
    execution_steps: list[str] = Field(default_factory=list)
    callback_requirements: list[str] = Field(default_factory=list)
    communication_tips: list[str] = Field(default_factory=list)
    raw_case_text: str | None = None
    review_status: str = "draft"
    priority: int = Field(default=100, ge=1, le=999)
    status: str = "active"


class ExpertPlaybookPatchRequest(BaseModel):
    title: str | None = None
    case_description: str | None = None
    trigger_keywords: list[str] | None = None
    primary_leaf_code: str | None = None
    primary_leaf_name: str | None = None
    product_tag_code: str | None = None
    product_tag_name: str | None = None
    request_tag_code: str | None = None
    request_tag_name: str | None = None
    verify_steps: list[str] | None = None
    judgment_rules: list[str] | None = None
    execution_steps: list[str] | None = None
    callback_requirements: list[str] | None = None
    communication_tips: list[str] | None = None
    raw_case_text: str | None = None
    review_status: str | None = None
    priority: int | None = Field(default=None, ge=1, le=999)
    status: str | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class UserCreateRequest(BaseModel):
    username: str = Field(min_length=2, max_length=80)
    password: str = Field(min_length=8, max_length=200)
    display_name: str | None = Field(default=None, max_length=120)
    role: Literal["admin", "operator", "viewer"] = "operator"
    status: Literal["active", "inactive", "locked"] = "active"


class UserPatchRequest(BaseModel):
    display_name: str | None = Field(default=None, max_length=120)
    role: Literal["admin", "operator", "viewer"] | None = None
    status: Literal["active", "inactive", "locked"] | None = None


class PasswordResetRequest(BaseModel):
    password: str = Field(min_length=8, max_length=200)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=200)
    new_password: str = Field(min_length=8, max_length=200)
