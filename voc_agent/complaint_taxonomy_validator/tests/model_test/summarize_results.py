from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from voc_agent.complaint_taxonomy_validator.tests.model_test.runner import OUTPUT_DIR


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize complaint taxonomy model test results.")
    parser.add_argument(
        "--summary-file",
        type=Path,
        help="Path to a specific summary JSON file. Defaults to the newest summary in output.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help="Directory containing summary artifacts.",
    )
    return parser


def find_latest_summary_file(output_dir: Path) -> Path:
    candidates = sorted(output_dir.glob("summary__*.json"))
    if not candidates:
        raise FileNotFoundError(f"No summary files found in {output_dir}")
    return candidates[-1]


def build_leaderboard_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for model_name, data in summary.get("per_model", {}).items():
        total_requests = int(data.get("total_requests", 0) or 0)
        json_valid_count = int(data.get("json_valid_count", 0) or 0)
        schema_valid_count = int(data.get("schema_valid_count", 0) or 0)
        avg_duration_ms = data.get("avg_duration_ms")
        rows.append(
            {
                "model_name": model_name,
                "total_requests": total_requests,
                "json_valid_count": json_valid_count,
                "schema_valid_count": schema_valid_count,
                "json_valid_rate": (json_valid_count / total_requests) if total_requests else 0.0,
                "schema_valid_rate": (schema_valid_count / total_requests) if total_requests else 0.0,
                "avg_duration_ms": avg_duration_ms,
            }
        )

    rows.sort(
        key=lambda row: (
            -row["schema_valid_rate"],
            -row["json_valid_rate"],
            row["avg_duration_ms"] if row["avg_duration_ms"] is not None else float("inf"),
            row["model_name"],
        )
    )
    return rows


def render_report(summary: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    lines = [
        f"Summary file: {summary['summary_path']}",
        f"Total models: {summary['total_models']}",
        f"Total cases: {summary['total_cases']}",
        f"Total requests: {summary['total_requests']}",
        f"Success count: {summary['success_count']}",
        f"Failure count: {summary['failure_count']}",
        f"JSON valid count: {summary['json_valid_count']}",
        f"Schema valid count: {summary['schema_valid_count']}",
        "",
        "Leaderboard",
        "rank | model | schema_valid | json_valid | avg_duration_ms",
    ]

    for index, row in enumerate(rows, start=1):
        lines.append(
            f"{index} | {row['model_name']} | "
            f"{row['schema_valid_count']}/{row['total_requests']} ({row['schema_valid_rate']:.0%}) | "
            f"{row['json_valid_count']}/{row['total_requests']} ({row['json_valid_rate']:.0%}) | "
            f"{row['avg_duration_ms']}"
        )

    return "\n".join(lines)


def load_summary(summary_file: Path) -> dict[str, Any]:
    summary = json.loads(summary_file.read_text(encoding="utf-8"))
    summary["summary_path"] = str(summary_file)
    return summary


def main() -> int:
    args = build_parser().parse_args()
    summary_file = args.summary_file or find_latest_summary_file(args.output_dir)
    summary = load_summary(summary_file)
    rows = build_leaderboard_rows(summary)
    print(render_report(summary, rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
