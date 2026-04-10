from __future__ import annotations

import os
from functools import lru_cache

# Disable LangSmith tracing by default for local runs unless explicitly enabled.
os.environ.setdefault("LANGCHAIN_TRACING_V2", "false")
os.environ.setdefault("LANGSMITH_TRACING", "false")
os.environ.setdefault("LANGCHAIN_CALLBACKS_BACKGROUND", "false")

from langchain_openai import ChatOpenAI

from voc_agent.core.config import get_settings


@lru_cache(maxsize=1)
def get_chat_model() -> ChatOpenAI:
    settings = get_settings()
    return ChatOpenAI(
        model=settings.llm_model_name,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        temperature=settings.llm_temperature,
    )
