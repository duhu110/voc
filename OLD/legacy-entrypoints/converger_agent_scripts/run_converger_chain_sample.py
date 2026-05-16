from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from voc_agent.converger_agent.chain import graph, run_converger  # noqa: E402


DEFAULT_TICKET_ID = "WeComQH20240601125916780935"


def _json_safe(value):
    if isinstance(value, (dt.datetime, dt.date)):
        return value.isoformat()
    return str(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run converger_agent chain on one ticket.")
    parser.add_argument("--ticket-id", default=DEFAULT_TICKET_ID, help="Ticket ID to analyze.")
    parser.add_argument(
        "--output-file",
        default=str(REPO_ROOT / "docs" / "converger_agent_design" / "converger_chain_sample.json"),
        help="Where to write the full graph state.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    full_state = graph.invoke({"ticket_id": args.ticket_id})
    result = run_converger(args.ticket_id)

    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(full_state, ensure_ascii=False, indent=2, default=_json_safe), encoding="utf-8")

    print(
        json.dumps(
            {
                "ticket_id": args.ticket_id,
                "status": result["status"],
                "primary_category": result["primary_category"],
                "request_tag": result["request_tag"],
                "emotion_tag": result["emotion_tag"],
                "risk_tag": result["risk_tag"],
                "product_tag": result["product_tag"],
                "line_category": result["line_category"],
                "resolution_summary": result["resolution_summary"],
                "output_file": str(output_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
