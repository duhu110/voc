#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-/home/voc}"
PYTHON_BIN="${REPO_ROOT}/.venv/bin/python"

if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "Python not found: ${PYTHON_BIN}" >&2
  exit 1
fi

cd "${REPO_ROOT}"

echo "[1/4] Effective settings"
"${PYTHON_BIN}" - <<'PY'
from voc_agent.core.config import get_settings

s = get_settings()
print("database_url_configured =", bool(s.database_url))
print("llm_base_url =", s.llm_base_url)
print("llm_model_name =", s.llm_model_name)
print("has_llm_api_key =", bool(s.llm_api_key))
print("vision_model_name =", s.vision_model_name)
print("has_vision_api_key =", bool(s.vision_api_key))
PY

echo "[2/4] Database connectivity"
"${PYTHON_BIN}" - <<'PY'
from sqlalchemy import text
from voc_agent.core.db import get_engine

with get_engine().connect() as conn:
    row = conn.execute(text("select current_database(), current_user")).first()
    print(row)
PY

echo "[3/4] Targeted tests"
"${PYTHON_BIN}" -m pytest voc_agent/advice_provider_agent/tests chainlit_app/tests -q

echo "[4/4] Chainlit import"
CHAINLIT_AUTH_SECRET="${CHAINLIT_AUTH_SECRET:-smoke-test-secret}" \
VOC_CHAINLIT_AUTH_USERS="${VOC_CHAINLIT_AUTH_USERS:-admin:secret}" \
"${PYTHON_BIN}" - <<'PY'
import chainlit_app.app
print("chainlit import ok")
PY
