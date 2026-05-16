from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from voc_agent.converger_agent.utils import (  # noqa: E402
    build_converger_messages,
    load_runtime_data,
    prompt_size_stats,
)
from voc_agent.share.tools import fetch_ticket  # noqa: E402


DEFAULT_TICKET_ID = "WeComQH20240601125916780935"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render one converger_agent prompt sample.")
    parser.add_argument("--ticket-id", default=DEFAULT_TICKET_ID, help="Ticket ID to render prompt for.")
    parser.add_argument(
        "--output-file",
        default=str(REPO_ROOT / "docs" / "converger_agent_design" / "prompt_sample.txt"),
        help="Where to write the rendered prompt.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    ticket = fetch_ticket(args.ticket_id)
    runtime_data = load_runtime_data()
    messages = build_converger_messages(ticket, runtime_data)
    stats = prompt_size_stats(messages)

    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "ticket_id": args.ticket_id,
        "stats": {
            "system_chars": stats.system_chars,
            "user_chars": stats.user_chars,
            "total_chars": stats.total_chars,
            "system_lines": stats.system_lines,
            "user_lines": stats.user_lines,
            "total_lines": stats.total_lines,
        },
        "messages": messages,
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "ticket_id": args.ticket_id,
                "output_file": str(output_path),
                "system_chars": stats.system_chars,
                "user_chars": stats.user_chars,
                "total_chars": stats.total_chars,
                "system_lines": stats.system_lines,
                "user_lines": stats.user_lines,
                "total_lines": stats.total_lines,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
