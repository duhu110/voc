from __future__ import annotations

import json
from pathlib import Path

from voc_agent.complaint_taxonomy_validator.tests.model_test.summarize_results import (
    build_leaderboard_rows,
    find_latest_summary_file,
)


def test_find_latest_summary_file_returns_newest_summary(tmp_path: Path) -> None:
    older = tmp_path / "summary__2026-04-10T14-00-00.json"
    newer = tmp_path / "summary__2026-04-10T15-00-00.json"
    older.write_text("{}", encoding="utf-8")
    newer.write_text("{}", encoding="utf-8")

    assert find_latest_summary_file(tmp_path) == newer


def test_build_leaderboard_rows_sorts_by_schema_rate_then_speed() -> None:
    summary = {
        "per_model": {
            "fast-but-less-valid": {
                "total_requests": 5,
                "json_valid_count": 3,
                "schema_valid_count": 3,
                "avg_duration_ms": 10000,
            },
            "stable-and-fast": {
                "total_requests": 5,
                "json_valid_count": 5,
                "schema_valid_count": 5,
                "avg_duration_ms": 15000,
            },
            "stable-but-slow": {
                "total_requests": 5,
                "json_valid_count": 5,
                "schema_valid_count": 5,
                "avg_duration_ms": 40000,
            },
        }
    }

    rows = build_leaderboard_rows(summary)

    assert [row["model_name"] for row in rows] == [
        "stable-and-fast",
        "stable-but-slow",
        "fast-but-less-valid",
    ]
    assert rows[0]["schema_valid_rate"] == 1.0
    assert rows[2]["json_valid_rate"] == 0.6
