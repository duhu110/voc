from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


def find_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgres://"):
        return "postgresql+psycopg://" + database_url[len("postgres://") :]
    if database_url.startswith("postgresql://"):
        return "postgresql+psycopg://" + database_url[len("postgresql://") :]
    return database_url


@lru_cache(maxsize=1)
def get_database_url() -> str:
    load_dotenv(find_repo_root() / ".env", override=False)
    database_url = (
        os.getenv("DATABASE_URL")
        or os.getenv("DATABASEURL")
        or os.getenv("DB_URL")
        or ""
    ).strip()
    if not database_url:
        raise RuntimeError("未找到数据库连接。请在项目根目录 .env 中设置 DATABASEURL 或 DATABASE_URL。")
    return normalize_database_url(database_url)


@st.cache_resource(show_spinner=False)
def get_engine() -> Engine:
    return create_engine(get_database_url(), future=True, pool_pre_ping=True)


@st.cache_data(ttl=60, show_spinner=False)
def query_df(sql: str) -> pd.DataFrame:
    with get_engine().connect() as connection:
        return pd.read_sql_query(text(sql), connection)
