from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


def find_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_project_env() -> None:
    repo_root = find_repo_root()
    load_dotenv(repo_root / '.env', override=False)
    load_dotenv(repo_root / 'voc_agent' / '.env', override=False)


def normalize_database_url(database_url: str) -> str:
    if database_url.startswith('postgres://'):
        return 'postgresql+psycopg://' + database_url[len('postgres://') :]
    if database_url.startswith('postgresql://'):
        return 'postgresql+psycopg://' + database_url[len('postgresql://') :]
    return database_url


@dataclass(frozen=True)
class Settings:
    repo_root: Path
    database_url: str
    llm_base_url: str
    llm_model_name: str
    llm_api_key: str
    llm_temperature: float = 0.0


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    load_project_env()
    repo_root = find_repo_root()

    database_url = (
        os.getenv('DATABASE_URL')
        or os.getenv('DATABASEURL')
        or os.getenv('DB_URL')
        or ''
    ).strip()
    if not database_url:
        raise RuntimeError('Missing database URL. Set DATABASEURL or DATABASE_URL in the repository root .env')
    database_url = normalize_database_url(database_url)

    llm_base_url = (os.getenv('VOC_LLM_BASE_URL') or os.getenv('BASE_URL') or '').strip()
    llm_model_name = (os.getenv('VOC_LLM_MODEL_NAME') or os.getenv('MODEL_NAME') or '').strip()
    llm_api_key = (os.getenv('VOC_LLM_API_KEY') or os.getenv('APP_KEY') or os.getenv('OPENAI_API_KEY') or '').strip()
    llm_temperature_raw = (os.getenv('VOC_LLM_TEMPERATURE') or '0').strip()

    if not llm_base_url:
        raise RuntimeError('Missing LLM base URL. Set VOC_LLM_BASE_URL in voc_agent/.env or environment')
    if not llm_model_name:
        raise RuntimeError('Missing LLM model name. Set VOC_LLM_MODEL_NAME in voc_agent/.env or environment')
    if not llm_api_key:
        raise RuntimeError('Missing LLM API key. Set VOC_LLM_API_KEY in voc_agent/.env or environment')

    return Settings(
        repo_root=repo_root,
        database_url=database_url,
        llm_base_url=llm_base_url,
        llm_model_name=llm_model_name,
        llm_api_key=llm_api_key,
        llm_temperature=float(llm_temperature_raw),
    )
