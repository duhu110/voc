#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import traceback
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


def json_default(value):
    if isinstance(value, (dt.datetime, dt.date)):
        return value.isoformat()
    return str(value)


def fetch_pending_ticket_ids(limit: int) -> list[str]:
    with get_engine().connect() as conn:
        return list(conn.execute(PENDING_TICKETS_SQL, {"limit": limit}).scalars().all())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run converger_agent with detailed per-ticket output.")
    parser.add_argument("--sample-size", type=int, default=1, help="Number of pending tickets to process.")
    parser.add_argument("--show-traceback", action="store_true", help="Print full traceback when a ticket fails.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.sample_size < 1:
        raise SystemExit("--sample-size must be >= 1")

    ticket_ids = fetch_pending_ticket_ids(args.sample_size)
    total = len(ticket_ids)
    success_count = 0
    failure_count = 0

    print(f"repo_root={REPO_ROOT}")
    print(f"requested_sample_size={args.sample_size}")
    print(f"fetched_pending_tickets={total}")

    for index, ticket_id in enumerate(ticket_ids, 1):
        print(f"\n[{index}/{total}] ticket_id={ticket_id}")
        try:
            payload = run_converger_and_persist(ticket_id)
            success_count += 1
            print(json.dumps(payload, ensure_ascii=False, indent=2, default=json_default))
        except Exception as exc:
            failure_count += 1
            print(f"status=ERROR")
            print(f"error_type={type(exc).__name__}")
            print(f"error={exc}")
            if args.show_traceback:
                traceback.print_exc()

    print(
        json.dumps(
            {
                "requested_sample_size": args.sample_size,
                "fetched_pending_tickets": total,
                "success_count": success_count,
                "failure_count": failure_count,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if failure_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
