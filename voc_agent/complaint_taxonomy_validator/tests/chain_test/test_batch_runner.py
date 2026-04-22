from __future__ import annotations

from pathlib import Path

from voc_agent.complaint_taxonomy_validator.tests.chain_test.runner import write_markdown_report


def test_write_markdown_report_contains_success_and_failure_counts(tmp_path: Path) -> None:
    summary = {
        "sample_size": 20,
        "success_count": 12,
        "failure_count": 8,
        "success_rate": 0.6,
        "failures_by_stage": {"chain": 5, "parse_retry": 3},
    }

    report_path = write_markdown_report(tmp_path, summary)
    report_text = report_path.read_text(encoding="utf-8")

    assert report_path.exists()
    assert "成功 12" in report_text
    assert "失败 8" in report_text
