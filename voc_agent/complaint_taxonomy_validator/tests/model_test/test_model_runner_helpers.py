from __future__ import annotations

import json
from pathlib import Path

from voc_agent.complaint_taxonomy_validator.tests.model_test.runner import (
    build_prompt_cases,
    parse_model_ids,
    select_target_models,
    validate_json_response,
    write_result_artifact,
)


def test_parse_model_ids_extracts_ids_from_model_list_text() -> None:
    raw_text = "id='DeepSeek-V3.2-Standard',\nid='Qwen3-32B',\n"

    assert parse_model_ids(raw_text) == ["DeepSeek-V3.2-Standard", "Qwen3-32B"]


def test_build_prompt_cases_returns_five_distinct_cases() -> None:
    sample_path = Path("voc_agent/complaint_taxonomy_validator/tests/prompt_sample_2024121013451359982515.txt")

    cases = build_prompt_cases(sample_path)

    assert len(cases) == 5
    assert len({case.name for case in cases}) == 5
    assert all(case.system_prompt for case in cases)
    assert all(case.user_prompt for case in cases)


def test_write_result_artifact_persists_json(tmp_path: Path) -> None:
    payload = {
        "case_name": "base_case",
        "model_name": "DeepSeek-V3.2-Standard",
        "prompt_path": "sample.txt",
        "status": "success",
        "error_type": None,
        "error_message": None,
        "duration_ms": 123,
        "timestamp": "2026-04-10T12:00:00",
    }

    artifact_path = write_result_artifact(tmp_path, payload)

    assert artifact_path.exists()
    assert json.loads(artifact_path.read_text(encoding="utf-8")) == payload


def test_select_target_models_resolves_exact_and_prefix_matches() -> None:
    available_models = [
        "Qwen3-Coder-480B-A35B-Instruct",
        "Qwen3-235B-A22B",
        "DeepSeek-V3.2",
        "Qwen3-Max",
        "Doubao-Seed-2.0-pro",
    ]

    selected = select_target_models(
        available_models,
        [
            "Qwen3-Coder-480B-A35B",
            "Qwen3-235B-A22B",
            "DeepSeek-V3.2",
            "Qwen3-Max",
            "Doubao-Seed-2.0-pro",
        ],
    )

    assert selected == [
        "Qwen3-Coder-480B-A35B-Instruct",
        "Qwen3-235B-A22B",
        "DeepSeek-V3.2",
        "Qwen3-Max",
        "Doubao-Seed-2.0-pro",
    ]


def test_validate_json_response_reports_schema_compliance() -> None:
    response_text = json.dumps(
        {
            "summary": "用户否认订购并要求取消。",
            "primary_category": {
                "code": "SUBSCRIBE_DENY",
                "full_name": "订购与退订争议/用户否认订购",
                "confidence": 0.91,
                "reason": "用户明确表示不知情办理。",
            },
            "candidate_categories": [],
            "candidate_tags": [],
            "category_keywords": [],
            "tag_keywords": [],
            "risks": [],
        },
        ensure_ascii=False,
    )

    validation = validate_json_response(response_text)

    assert validation["is_json_object"] is True
    assert validation["required_keys_valid"] is True
    assert validation["primary_category_valid"] is True
