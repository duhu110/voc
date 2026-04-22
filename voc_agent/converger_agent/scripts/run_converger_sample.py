from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from voc_agent.converger_agent.nodes import analyze_controlled_tags, analyze_primary_category  # noqa: E402
from voc_agent.converger_agent.nodes import summarize_resolution  # noqa: E402
from voc_agent.share.tools import fetch_ticket  # noqa: E402


DEFAULT_TICKET_ID = "WeComQH20240601125916780935"


def _json_safe(value):
    if isinstance(value, (dt.datetime, dt.date)):
        return value.isoformat()
    return str(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run converger_agent primary category + controlled tags on one ticket.")
    parser.add_argument("--ticket-id", default=DEFAULT_TICKET_ID, help="Ticket ID to analyze.")
    parser.add_argument(
        "--output-file",
        default=str(REPO_ROOT / "docs" / "converger_agent_design" / "converger_sample.json"),
        help="Where to write the node output.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    ticket = fetch_ticket(args.ticket_id)
    state = {"ticket_id": args.ticket_id, "ticket": ticket}
    state.update(analyze_primary_category(state))
    state.update(analyze_controlled_tags(state))
    state.update(summarize_resolution(state))

    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(state, ensure_ascii=False, indent=2, default=_json_safe), encoding="utf-8")

    print(
        json.dumps(
            {
                "ticket_id": args.ticket_id,
                "status": state["status"],
                "primary_category": state["primary_category"],
                "request_tag": state["request_tag"],
                "emotion_tag": state["emotion_tag"],
                "risk_tag": state["risk_tag"],
                "product_tag": state["product_tag"],
                "line_category": state["line_category"],
                "resolution_summary": state["resolution_summary"],
                "output_file": str(output_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
