#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


STATUS_SQL = """
select
  count(*) filter (where converger_agent_status = true) as processed_count,
  count(*) filter (where converger_agent_status = false) as pending_count,
  count(*) as total_count
from raw_complaint_tickets
"""


def find_repo_root() -> Path:
    current = Path(__file__).resolve()
    for path in [current.parent, *current.parents]:
        if (path / "pyproject.toml").exists() and (path / "voc_agent").exists():
            return path
    raise RuntimeError("Could not find project root containing pyproject.toml and voc_agent")


def find_run_sql(repo_root: Path, explicit_path: str | None) -> Path:
    candidates: list[Path] = []
    if explicit_path:
        candidates.append(Path(explicit_path))
    candidates.extend(
        [
            repo_root / "scripts" / "run_sql.py",
            Path(__file__).resolve().parent / "run_sql.py",
        ]
    )

    for candidate in candidates:
        path = candidate if candidate.is_absolute() else repo_root / candidate
        if path.exists():
            return path

    searched = ", ".join(str(item) for item in candidates)
    raise RuntimeError(f"Could not find run_sql.py. Searched: {searched}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Count processed and pending converger_agent tickets.")
    parser.add_argument("--run-sql", default=None, help="Path to run_sql.py. Defaults to scripts/run_sql.py.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = find_repo_root()
    run_sql = find_run_sql(repo_root, args.run_sql)

    command = [sys.executable, str(run_sql), "--sql", STATUS_SQL]
    print(f"repo_root={repo_root}")
    print(f"run_sql={run_sql}")
    completed = subprocess.run(command, cwd=repo_root)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
