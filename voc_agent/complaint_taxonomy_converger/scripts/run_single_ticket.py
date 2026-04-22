from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

os.environ.setdefault('LANGCHAIN_TRACING_V2', 'false')
os.environ.setdefault('LANGSMITH_TRACING', 'false')
os.environ.setdefault('LANGCHAIN_CALLBACKS_BACKGROUND', 'false')

from voc_agent.complaint_taxonomy_converger.chain import run_converger
from voc_agent.complaint_taxonomy_converger.tools import fetch_random_pending_ticket_ids


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Run one complaint_taxonomy_converger ticket.')
    parser.add_argument('--ticket-id', help='Ticket ID to run')
    parser.add_argument('--random-pending', action='store_true', help='Pick one random pending ticket')
    return parser


def main() -> None:
    args = build_parser().parse_args()
    ticket_id = args.ticket_id
    if not ticket_id:
        if not args.random_pending:
            raise SystemExit('Provide --ticket-id or use --random-pending')
        ids = fetch_random_pending_ticket_ids(limit=1)
        if not ids:
            raise SystemExit('No pending ticket found')
        ticket_id = ids[0]

    print(json.dumps(run_converger(ticket_id), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
