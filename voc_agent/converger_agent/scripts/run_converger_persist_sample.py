from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sqlalchemy import text

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from voc_agent.converger_agent.persistence import run_converger_and_persist  # noqa: E402
from voc_agent.core.db import get_engine  # noqa: E402

RANDOM_CONVERGER_PENDING_QUERY = text(
    """
    select ticket_id
    from raw_complaint_tickets
    where converger_agent_status = false
    order by random()
    limit :limit
    """
)


def fetch_random_converger_pending_ids(limit: int = 20) -> list[str]:
    """Fetch random ticket IDs not yet processed by converger agent."""
    with get_engine().connect() as conn:
        rows = conn.execute(RANDOM_CONVERGER_PENDING_QUERY, {"limit": limit}).scalars().all()
    return list(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run converger agent on random pending tickets.")
    parser.add_argument(
        "--sample-size",
        type=int,
        default=20,
        help="Number of random pending tickets to process (default: 20).",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    ticket_ids = fetch_random_converger_pending_ids(args.sample_size)
    total = len(ticket_ids)
    print(f"Fetched {total} pending tickets to process.")

    for idx, ticket_id in enumerate(ticket_ids, 1):
        print(f"\n[{idx}/{total}] Processing {ticket_id} ...")
        try:
            result = run_converger_and_persist(ticket_id)
            print(json.dumps(result["write_summary"], ensure_ascii=False))
        except Exception as exc:
            print(f"  ERROR: {exc}")

    print(f"\nDone. Processed {total} tickets.")


if __name__ == "__main__":
    main()
