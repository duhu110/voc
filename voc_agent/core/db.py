from __future__ import annotations

from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from voc_agent.core.config import get_settings


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Return the shared SQLAlchemy engine for all agents."""
    settings = get_settings()
    return create_engine(settings.database_url, future=True)
