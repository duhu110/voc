from __future__ import annotations

from typing import Any

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

