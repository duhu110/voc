# Complaint Taxonomy Validator Model Test Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a pytest suite that reads configured models and prompt cases, calls the OpenAI-compatible endpoint directly, and writes result artifacts into the model test output directory.

**Architecture:** Add a focused helper module in `model_test` for parsing inputs, building prompt cases, invoking the OpenAI client, and writing artifacts. Cover parsing and prompt generation with fast pytest tests first, then add a live integration pytest that uses the helper and records a summary.

**Tech Stack:** Python 3.13, pytest, OpenAI SDK, python-dotenv via existing config loader, JSON file output

---

### Task 1: Add failing tests for model list parsing and prompt generation

**Files:**
- Create: `voc_agent/complaint_taxonomy_validator/tests/model_test/test_model_runner_helpers.py`
- Test: `voc_agent/complaint_taxonomy_validator/tests/model_test/test_model_runner_helpers.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from voc_agent.complaint_taxonomy_validator.tests.model_test.runner import (
    build_prompt_cases,
    parse_model_ids,
)


def test_parse_model_ids_extracts_ids_from_model_list_text() -> None:
    raw_text = "id='DeepSeek-V3.2-Standard',\nid='Qwen3-32B',\n"

    assert parse_model_ids(raw_text) == ["DeepSeek-V3.2-Standard", "Qwen3-32B"]


def test_build_prompt_cases_returns_five_cases() -> None:
    sample_path = Path("voc_agent/complaint_taxonomy_validator/tests/prompt_sample_2024121013451359982515.txt")

    cases = build_prompt_cases(sample_path)

    assert len(cases) == 5
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest voc_agent/complaint_taxonomy_validator/tests/model_test/test_model_runner_helpers.py -q`
Expected: FAIL because `runner` module does not exist yet

- [ ] **Step 3: Write minimal implementation**

Create `runner.py` with:

```python
def parse_model_ids(raw_text: str) -> list[str]:
    ...


def build_prompt_cases(sample_path: Path) -> list[PromptCase]:
    ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.\.venv\Scripts\python.exe -m pytest voc_agent/complaint_taxonomy_validator/tests/model_test/test_model_runner_helpers.py -q`
Expected: PASS

### Task 2: Add failing tests for result artifact writing

**Files:**
- Modify: `voc_agent/complaint_taxonomy_validator/tests/model_test/test_model_runner_helpers.py`
- Modify: `voc_agent/complaint_taxonomy_validator/tests/model_test/runner.py`

- [ ] **Step 1: Write the failing test**

```python
def test_write_result_artifact_persists_json(tmp_path: Path) -> None:
    result = {
        "case_name": "base_case",
        "model_name": "DeepSeek-V3.2-Standard",
        "prompt_path": "sample.txt",
        "status": "success",
        "error_type": None,
        "error_message": None,
        "duration_ms": 123,
        "timestamp": "2026-04-10T12:00:00",
    }

    artifact_path = write_result_artifact(tmp_path, result)

    assert artifact_path.exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest voc_agent/complaint_taxonomy_validator/tests/model_test/test_model_runner_helpers.py -q`
Expected: FAIL because `write_result_artifact` is missing

- [ ] **Step 3: Write minimal implementation**

Add `write_result_artifact()` that creates the directory and dumps JSON.

- [ ] **Step 4: Run test to verify it passes**

Run: `.\.venv\Scripts\python.exe -m pytest voc_agent/complaint_taxonomy_validator/tests/model_test/test_model_runner_helpers.py -q`
Expected: PASS

### Task 3: Add the live OpenAI integration pytest

**Files:**
- Create: `voc_agent/complaint_taxonomy_validator/tests/model_test/test_openai_model_responses.py`
- Modify: `voc_agent/complaint_taxonomy_validator/tests/model_test/runner.py`

- [ ] **Step 1: Write the failing test**

```python
def test_live_openai_models_generate_and_persist_outputs() -> None:
    summary = run_model_suite()
    assert summary["total_requests"] > 0
    assert not summary["failures"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest voc_agent/complaint_taxonomy_validator/tests/model_test/test_openai_model_responses.py -q`
Expected: FAIL because `run_model_suite` is missing

- [ ] **Step 3: Write minimal implementation**

Add `run_model_suite()` to:

```python
- load settings
- parse models
- build five prompt cases
- call `OpenAI(...).chat.completions.create(...)`
- write success and failure artifacts
- write a summary JSON
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.\.venv\Scripts\python.exe -m pytest voc_agent/complaint_taxonomy_validator/tests/model_test/test_openai_model_responses.py -q -s`
Expected: PASS if all requests succeed, otherwise FAIL after writing failure artifacts

### Task 4: Verify the complete model test suite

**Files:**
- Test: `voc_agent/complaint_taxonomy_validator/tests/model_test/test_model_runner_helpers.py`
- Test: `voc_agent/complaint_taxonomy_validator/tests/model_test/test_openai_model_responses.py`

- [ ] **Step 1: Run the focused suite**

Run: `.\.venv\Scripts\python.exe -m pytest voc_agent/complaint_taxonomy_validator/tests/model_test -q -s`
Expected: Helper tests pass, live integration executes, output artifacts written

- [ ] **Step 2: Inspect generated files**

Check: `voc_agent/complaint_taxonomy_validator/tests/model_test/output`
Expected: per-request JSON files and one summary JSON file exist
