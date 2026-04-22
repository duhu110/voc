from __future__ import annotations

from pathlib import Path

from voc_agent.complaint_taxonomy_validator.tests.chain_test.runner import run_chain_batch_validation


def test_run_chain_batch_validation_writes_summary_for_20_tickets() -> None:
    summary = run_chain_batch_validation(sample_size=20)

    assert summary["sample_size"] == 20
    assert summary["success_count"] + summary["failure_count"] == 20
    assert Path(summary["summary_path"]).exists()
    assert Path(summary["report_path"]).exists()
