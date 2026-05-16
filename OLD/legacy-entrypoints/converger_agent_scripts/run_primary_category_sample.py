from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from voc_agent.converger_agent.nodes import analyze_primary_category  # noqa: E402
from voc_agent.share.tools import fetch_ticket  # noqa: E402


DEFAULT_TICKET_ID = "WeComQH20240601125916780935"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run converger_agent primary category node on one ticket.")
    parser.add_argument("--ticket-id", default=DEFAULT_TICKET_ID, help="Ticket ID to analyze.")
    parser.add_argument(
        "--output-file",
        default=str(REPO_ROOT / "docs" / "converger_agent_design" / "primary_category_sample.json"),
        help="Where to write the node output.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    ticket = fetch_ticket(args.ticket_id)
    result = analyze_primary_category({"ticket_id": args.ticket_id, "ticket": ticket})
    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "ticket_id": args.ticket_id,
                "status": result["status"],
                "primary_category": result["primary_category"],
                "output_file": str(output_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
