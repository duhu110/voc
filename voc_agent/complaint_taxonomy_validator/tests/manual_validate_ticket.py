from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

os.environ.setdefault("LANGCHAIN_TRACING_V2", "false")
os.environ.setdefault("LANGSMITH_TRACING", "false")
os.environ.setdefault("LANGCHAIN_CALLBACKS_BACKGROUND", "false")

from langchain_core.messages import HumanMessage, SystemMessage

from voc_agent.complaint_taxonomy_validator.prompts import SYSTEM_PROMPT, build_user_prompt
from voc_agent.complaint_taxonomy_validator.state import ValidatorOutput
from voc_agent.complaint_taxonomy_validator.tools import fetch_sample_ticket_ids
from voc_agent.complaint_taxonomy_validator.utils import normalize_result
from voc_agent.core.llm import get_chat_model
from voc_agent.share.tools import fetch_enabled_categories, fetch_enabled_tags, fetch_ticket
from voc_agent.share.utils import extract_json_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Manual terminal runner for complaint_taxonomy_validator with full raw output retention.'
    )
    parser.add_argument('--ticket-id', help='Ticket ID to validate')
    parser.add_argument('--latest', action='store_true', help='Use the latest ticket ID from raw_complaint_tickets')
    parser.add_argument('--show-prompt', action='store_true', help='Print the full prompt before calling the model')
    parser.add_argument(
        '--save-dir',
        default='voc_agent/complaint_taxonomy_validator/tests/output',
        help='Directory to save the full debug output JSON',
    )
    return parser


def resolve_ticket_id(ticket_id: str | None, use_latest: bool) -> str:
    if ticket_id:
        return ticket_id
    if use_latest:
        ids = fetch_sample_ticket_ids(limit=1)
        if not ids:
            raise RuntimeError('No ticket IDs found in raw_complaint_tickets')
        return ids[0]
    raise RuntimeError('Provide --ticket-id or use --latest')


def build_debug_payload(ticket_id: str, raw_text: str, raw_json_text: str, raw_data: dict[str, Any], normalized: dict[str, Any]) -> dict[str, Any]:
    return {
        'ticket_id': ticket_id,
        'timestamp': datetime.now().isoformat(timespec='seconds'),
        'raw_response_text': raw_text,
        'raw_json_text': raw_json_text,
        'raw_data': raw_data,
        'normalized_output': normalized,
    }


def main() -> None:
    args = build_parser().parse_args()
    ticket_id = resolve_ticket_id(args.ticket_id, args.latest)

    ticket = fetch_ticket(ticket_id)
    categories = fetch_enabled_categories()
    tags = fetch_enabled_tags()
    prompt = build_user_prompt(ticket=ticket, categories=categories, tags=tags)

    if args.show_prompt:
        print('===== SYSTEM PROMPT =====')
        print(SYSTEM_PROMPT)
        print('\n===== USER PROMPT =====')
        print(prompt)
        print('\n===== END PROMPT =====\n')

    llm = get_chat_model()
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt + '\n\n请只返回纯 JSON，不要使用 Markdown 代码块。'),
    ])

    raw_text = response.text if hasattr(response, 'text') else str(response.content)
    raw_json_text = extract_json_text(raw_text)

    try:
        raw_data = json.loads(raw_json_text)
    except json.JSONDecodeError as exc:
        debug_payload = {
            'ticket_id': ticket_id,
            'timestamp': datetime.now().isoformat(timespec='seconds'),
            'raw_response_text': raw_text,
            'raw_json_text': raw_json_text,
            'json_decode_error': str(exc),
        }
        save_debug_output(debug_payload, args.save_dir, ticket_id)
        print('===== RAW RESPONSE =====')
        print(raw_text)
        print('\n===== JSON DECODE ERROR =====')
        print(exc)
        raise SystemExit(1)

    normalized = normalize_result(raw_data, categories, tags)
    parsed = ValidatorOutput.model_validate(normalized)
    debug_payload = build_debug_payload(
        ticket_id=ticket_id,
        raw_text=raw_text,
        raw_json_text=raw_json_text,
        raw_data=raw_data,
        normalized=parsed.model_dump(mode='json'),
    )
    output_path = save_debug_output(debug_payload, args.save_dir, ticket_id)

    print('===== RAW RESPONSE =====')
    print(raw_text)
    print('\n===== NORMALIZED OUTPUT =====')
    print(json.dumps(parsed.model_dump(mode='json'), ensure_ascii=False, indent=2))
    print(f'\nSaved full output to: {output_path}')


def save_debug_output(payload: dict[str, Any], save_dir: str, ticket_id: str) -> Path:
    output_dir = Path(save_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / f'{ticket_id}.json'
    file_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    return file_path


if __name__ == '__main__':
    main()
