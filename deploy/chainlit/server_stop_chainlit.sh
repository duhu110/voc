#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-/home/voc}"
PID_FILE="${REPO_ROOT}/deploy/chainlit/runtime/chainlit.pid"

if [[ ! -f "${PID_FILE}" ]]; then
  echo "No PID file found: ${PID_FILE}"
  exit 0
fi

PID="$(cat "${PID_FILE}")"
if ps -p "${PID}" >/dev/null 2>&1; then
  kill "${PID}"
  sleep 1
fi

rm -f "${PID_FILE}"
echo "Stopped Chainlit PID ${PID}"
