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

from voc_agent.advice_provider_agent.provider import dumps_provider_result, run_advice_provider  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate handling advice for one ticket.")
    parser.add_argument("--ticket-id", required=True, help="raw_complaint_tickets.ticket_id")
    parser.add_argument(
        "--use-existing-classification",
        action="store_true",
        help="Use existing converger_agent_result instead of re-running classification.",
    )
    parser.add_argument(
        "--include-processing-context",
        action="store_true",
        help="Keep historical processing fields. Default hides them for new-ticket simulation.",
    )
    parser.add_argument("--advice-limit", type=int, default=5)
    parser.add_argument("--sample-limit", type=int, default=5)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = run_advice_provider(
        args.ticket_id,
        use_existing_classification=args.use_existing_classification,
        hide_processing_context=not args.include_processing_context,
        advice_limit=args.advice_limit,
        sample_limit=args.sample_limit,
    )
    print(dumps_provider_result(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
