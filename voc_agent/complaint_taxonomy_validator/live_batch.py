from __future__ import annotations

import argparse
import json
import time
import traceback
from collections import Counter
from datetime import datetime
from typing import Any

from voc_agent.complaint_taxonomy_validator.persistence import run_validator_and_persist
from voc_agent.complaint_taxonomy_validator.tools import fetch_pending_ticket_ids
from voc_agent.core.config import get_settings


def run_live_batch(sample_size: int = 500) -> dict[str, Any]:
    settings = get_settings()
    ticket_ids = fetch_pending_ticket_ids(limit=sample_size)
    if len(ticket_ids) != sample_size:
        raise RuntimeError(f'Expected {sample_size} pending ticket IDs, got {len(ticket_ids)}')

    failures_by_stage: Counter[str] = Counter()
    summary: dict[str, Any] = {
        'timestamp': datetime.now().isoformat(timespec='seconds'),
        'sample_size': sample_size,
        'model_name': settings.llm_model_name,
        'ticket_ids': ticket_ids,
        'success_count': 0,
        'failure_count': 0,
        'success_rate': 0.0,
        'failures_by_stage': {},
        'results': [],
    }

    for ticket_id in ticket_ids:
        started_at = time.perf_counter()
        try:
            persisted = run_validator_and_persist(ticket_id)
            payload = {
                'ticket_id': ticket_id,
                'status': 'success',
                'stage': 'persistence',
                'duration_ms': int((time.perf_counter() - started_at) * 1000),
                'timestamp': datetime.now().isoformat(timespec='seconds'),
                'model_name': settings.llm_model_name,
                'write_summary': persisted['write_summary'],
            }
            summary['success_count'] += 1
        except Exception as exc:  # noqa: BLE001
            failures_by_stage['persistence'] += 1
            payload = {
                'ticket_id': ticket_id,
                'status': 'failed',
                'stage': 'persistence',
                'duration_ms': int((time.perf_counter() - started_at) * 1000),
                'timestamp': datetime.now().isoformat(timespec='seconds'),
                'model_name': settings.llm_model_name,
                'error_type': exc.__class__.__name__,
                'error_message': str(exc),
                'traceback': ''.join(traceback.format_exception(exc)),
            }
            summary['failure_count'] += 1

        summary['results'].append(payload)

    summary['success_rate'] = summary['success_count'] / sample_size if sample_size else 0.0
    summary['failures_by_stage'] = dict(failures_by_stage)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Run complaint_taxonomy_validator batch directly without writing artifacts.')
    parser.add_argument('--sample-size', type=int, default=500, help='Number of unprocessed tickets to run.')
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = run_live_batch(sample_size=args.sample_size)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
