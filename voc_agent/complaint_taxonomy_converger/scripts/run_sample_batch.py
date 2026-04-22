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
    parser = argparse.ArgumentParser(description='Run complaint_taxonomy_converger sample batch without database writes.')
    parser.add_argument('--sample-size', type=int, default=20, help='Number of random pending tickets to run.')
    return parser


def main() -> None:
    args = build_parser().parse_args()
    ticket_ids = fetch_random_pending_ticket_ids(limit=args.sample_size)
    if len(ticket_ids) != args.sample_size:
        raise SystemExit(f'Expected {args.sample_size} pending tickets, got {len(ticket_ids)}')

    results = []
    category_found_count = 0
    tag_found_count = 0
    skipped_count = 0

    for ticket_id in ticket_ids:
        result = run_converger(ticket_id)
        results.append(result)
        if result['primary_category']:
            category_found_count += 1
        else:
            skipped_count += 1
        if result['selected_tags']:
            tag_found_count += 1

    summary = {
        'sample_size': args.sample_size,
        'category_found_count': category_found_count,
        'tag_found_count': tag_found_count,
        'skipped_no_category_count': skipped_count,
        'ticket_ids': ticket_ids,
        'results': results,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
