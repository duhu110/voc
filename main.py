from __future__ import annotations

import argparse
import json

from voc_agent.complaint_taxonomy_validator import run_validator
from voc_agent.complaint_taxonomy_validator.tools import fetch_sample_ticket_ids


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='VOC agent runtime')
    subparsers = parser.add_subparsers(dest='command', required=True)

    validate = subparsers.add_parser('validate-ticket', help='Validate one raw complaint ticket against taxonomy')
    validate.add_argument('--ticket-id', required=True, help='Ticket ID from raw_complaint_tickets')

    sample = subparsers.add_parser('sample-ticket-ids', help='Show recent ticket IDs for testing')
    sample.add_argument('--limit', type=int, default=5, help='Number of ticket IDs to return')

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == 'validate-ticket':
        result = run_validator(args.ticket_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.command == 'sample-ticket-ids':
        result = fetch_sample_ticket_ids(limit=args.limit)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    parser.error(f'Unsupported command: {args.command}')


if __name__ == '__main__':
    main()
