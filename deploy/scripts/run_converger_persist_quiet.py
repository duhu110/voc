#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sqlalchemy import text


def find_repo_root() -> Path:
    current = Path(__file__).resolve()
    for path in [current.parent, *current.parents]:
        if (path / "pyproject.toml").exists() and (path / "voc_agent").exists():
            return path
    raise RuntimeError("Could not find project root containing pyproject.toml and voc_agent")


REPO_ROOT = find_repo_root()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from voc_agent.converger_agent.persistence import run_converger_and_persist  # noqa: E402
from voc_agent.core.db import get_engine  # noqa: E402


PENDING_TICKETS_SQL = text(
    """
    select ticket_id
    from raw_complaint_tickets
    where converger_agent_status = false
    order by random()
    limit :limit
    """
)


def fetch_pending_ticket_ids(limit: int) -> list[str]:
    with get_engine().connect() as conn:
        return list(conn.execute(PENDING_TICKETS_SQL, {"limit": limit}).scalars().all())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run converger_agent with compact output.")
    parser.add_argument("--sample-size", type=int, default=1, help="Number of pending tickets to process.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.sample_size < 1:
        raise SystemExit("--sample-size must be >= 1")

    ticket_ids = fetch_pending_ticket_ids(args.sample_size)
    total = len(ticket_ids)
    success_count = 0
    failure_count = 0

    print(f"Fetched {total} pending tickets.")
    for index, ticket_id in enumerate(ticket_ids, 1):
        try:
            summary = run_converger_and_persist(ticket_id)["write_summary"]
            success_count += 1
            print(
                f"[{index}/{total}] OK ticket_id={ticket_id} "
                f"result_rows={summary['result_rows']} "
                f"resolution_summary_rows={summary['resolution_summary_rows']}"
            )
        except Exception as exc:
            failure_count += 1
            print(f"[{index}/{total}] ERROR ticket_id={ticket_id} {type(exc).__name__}: {exc}")

    print(f"Done. success={success_count} failure={failure_count} fetched={total}")
    return 0 if failure_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
