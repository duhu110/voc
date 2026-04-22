#!/usr/bin/env bash
set -euo pipefail

SAMPLE_SIZE="${1:-500}"

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_EXE="$REPO_ROOT/.venv/bin/python"

if [ ! -f "$PYTHON_EXE" ]; then
    echo "Python virtual environment not found at $PYTHON_EXE" >&2
    exit 1
fi

cd "$REPO_ROOT"
"$PYTHON_EXE" -m voc_agent.converger_agent.scripts.run_converger_persist_sample --sample-size "$SAMPLE_SIZE"
