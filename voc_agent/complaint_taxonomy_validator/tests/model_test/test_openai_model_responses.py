from __future__ import annotations

from pathlib import Path

from voc_agent.complaint_taxonomy_validator.tests.model_test.runner import run_model_suite


def test_live_openai_models_generate_and_persist_outputs() -> None:
    summary = run_model_suite()

    assert summary["total_models"] == 5
    assert summary["total_cases"] == 5
    assert summary["total_requests"] == 25
    assert "json_valid_count" in summary
    assert "schema_valid_count" in summary
    assert Path(summary["summary_path"]).exists()
