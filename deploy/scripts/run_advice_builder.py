#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def find_repo_root() -> Path:
    current = Path(__file__).resolve()
    for path in [current.parent, *current.parents]:
        if (path / "pyproject.toml").exists() and (path / "voc_agent").exists():
            return path
    raise RuntimeError("Could not find project root containing pyproject.toml and voc_agent")


REPO_ROOT = find_repo_root()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from voc_agent.advice_builder_agent import build_advice_for_top_scopes  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build converger_handling_advice from converger_resolution_summary_atomic."
    )
    parser.add_argument("--limit", type=int, default=10, help="Number of high-frequency scopes to process.")
    parser.add_argument(
        "--min-summary-count",
        type=int,
        default=50,
        help="Only process scopes with at least this many resolution summaries.",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=30,
        help="Number of recent resolution summaries to send to the model per scope.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write advice rows. Without this flag the script only prints dry-run output.",
    )
    parser.add_argument(
        "--include-existing",
        action="store_true",
        help="Also rebuild scopes that already have active handling advice.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.limit < 1:
        raise SystemExit("--limit must be >= 1")
    if args.min_summary_count < 1:
        raise SystemExit("--min-summary-count must be >= 1")
    if args.sample_size < 1:
        raise SystemExit("--sample-size must be >= 1")

    summary = build_advice_for_top_scopes(
        limit=args.limit,
        min_summary_count=args.min_summary_count,
        sample_size=args.sample_size,
        dry_run=not args.write,
        skip_existing=not args.include_existing,
    )
    print(
        "Done. "
        f"scanned_scopes={summary.scanned_scopes} "
        f"generated_advice={summary.generated_advice} "
        f"written_advice={summary.written_advice} "
        f"failed_scopes={summary.failed_scopes}"
    )
    return 0 if summary.failed_scopes == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
