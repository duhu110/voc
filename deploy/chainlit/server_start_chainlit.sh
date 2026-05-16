#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-/home/voc}"
PORT="${2:-8883}"
APP_DIR="${REPO_ROOT}/chainlit_app"
PYTHON_BIN="${REPO_ROOT}/.venv/bin/python"
LOG_DIR="${REPO_ROOT}/deploy/chainlit/runtime"
PID_FILE="${LOG_DIR}/chainlit.pid"
LOG_FILE="${LOG_DIR}/chainlit.log"

mkdir -p "${LOG_DIR}"

if [[ -f "${PID_FILE}" ]]; then
  OLD_PID="$(cat "${PID_FILE}")"
  if ps -p "${OLD_PID}" >/dev/null 2>&1; then
    echo "Chainlit already running with PID ${OLD_PID}" >&2
    exit 1
  fi
  rm -f "${PID_FILE}"
fi

cd "${APP_DIR}"
nohup "${PYTHON_BIN}" -m chainlit run ./app.py --host 0.0.0.0 --port "${PORT}" --headless >"${LOG_FILE}" 2>&1 &
echo $! > "${PID_FILE}"
sleep 3

echo "Started Chainlit"
echo "PID: $(cat "${PID_FILE}")"
echo "Log: ${LOG_FILE}"
echo "URL: http://0.0.0.0:${PORT}"
