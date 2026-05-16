# Complaint Taxonomy Validator Chain Batch Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a chain-focused batch validation flow that samples 20 tickets from `raw_complaint_tickets`, runs the real `run_validator(ticket_id)` path, applies one extra parsing attempt when the model output is malformed, and writes JSON plus Markdown reports for later database-write readiness assessment.

**Architecture:** Keep the real validator chain as the execution path and strengthen its parsing step with a single fallback parse method. Add a dedicated batch validation helper under the complaint taxonomy validator tests area that selects random ticket IDs, runs the chain ticket-by-ticket without aborting the batch on failures, and writes per-ticket artifacts plus aggregate reports.

**Tech Stack:** Python 3.13, pytest, LangGraph chain, OpenAI-compatible provider through existing env, SQLAlchemy, JSON/Markdown report output

---

### Task 1: Add failing tests for single fallback parse behavior

**Files:**
- Create: `voc_agent/complaint_taxonomy_validator/tests/test_response_parsing.py`
- Modify: `voc_agent/share/utils/text_parsing.py`
- Modify: `voc_agent/complaint_taxonomy_validator/nodes/analyze_ticket.py`

- [ ] **Step 1: Write the failing test**

```python
import json

from voc_agent.share.utils import parse_json_payload_once


def test_parse_json_payload_once_recovers_json_wrapped_in_extra_text() -> None:
    raw_text = "说明如下\\n```json\\n{\"summary\": \"ok\", \"primary_category\": {\"code\": \"A\", \"full_name\": \"B\", \"confidence\": 0.9, \"reason\": \"x\"}, \"candidate_categories\": [], \"candidate_tags\": [], \"category_keywords\": [], \"tag_keywords\": [], \"risks\": []}\\n```\\n后续说明"

    parsed = parse_json_payload_once(raw_text)

    assert parsed["summary"] == "ok"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest voc_agent/complaint_taxonomy_validator/tests/test_response_parsing.py -q`
Expected: FAIL because `parse_json_payload_once` does not exist yet

- [ ] **Step 3: Write minimal implementation**

Add `parse_json_payload_once()` that:

```python
- first uses current `extract_json_text`
- then attempts `json.loads`
- if that fails, performs one extra cleanup/extraction pass
- raises the original parsing error if the fallback still fails
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.\.venv\Scripts\python.exe -m pytest voc_agent/complaint_taxonomy_validator/tests/test_response_parsing.py -q`
Expected: PASS

### Task 2: Add failing tests for batch report generation

**Files:**
- Create: `voc_agent/complaint_taxonomy_validator/tests/chain_test/test_batch_runner.py`
- Create: `voc_agent/complaint_taxonomy_validator/tests/chain_test/runner.py`

- [ ] **Step 1: Write the failing test**

```python
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

    assert report_path.exists()
    assert "success_count" not in report_path.read_text(encoding="utf-8")
    assert "12" in report_path.read_text(encoding="utf-8")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest voc_agent/complaint_taxonomy_validator/tests/chain_test/test_batch_runner.py -q`
Expected: FAIL because the runner module does not exist yet

- [ ] **Step 3: Write minimal implementation**

Create runner helpers that can:

```python
- create output directories
- persist per-ticket JSON results
- persist aggregate summary JSON
- render a Markdown report
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.\.venv\Scripts\python.exe -m pytest voc_agent/complaint_taxonomy_validator/tests/chain_test/test_batch_runner.py -q`
Expected: PASS

### Task 3: Add chain batch execution helper and live validation test

**Files:**
- Modify: `voc_agent/complaint_taxonomy_validator/tools/__init__.py`
- Create: `voc_agent/complaint_taxonomy_validator/tools/fetch_random_ticket_ids.py`
- Modify: `voc_agent/complaint_taxonomy_validator/tests/chain_test/runner.py`
- Create: `voc_agent/complaint_taxonomy_validator/tests/chain_test/test_live_chain_batch.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from voc_agent.complaint_taxonomy_validator.tests.chain_test.runner import run_chain_batch_validation


def test_run_chain_batch_validation_writes_summary_for_20_tickets() -> None:
    summary = run_chain_batch_validation(sample_size=20)

    assert summary["sample_size"] == 20
    assert summary["success_count"] + summary["failure_count"] == 20
    assert Path(summary["summary_path"]).exists()
    assert Path(summary["report_path"]).exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest voc_agent/complaint_taxonomy_validator/tests/chain_test/test_live_chain_batch.py -q -s`
Expected: FAIL because `run_chain_batch_validation` is missing

- [ ] **Step 3: Write minimal implementation**

Implement `run_chain_batch_validation()` to:

```python
- sample 20 random ticket IDs from `raw_complaint_tickets`
- invoke `run_validator(ticket_id)` for each ticket
- if chain parse fails, perform one extra parsing attempt using the same raw model response cleanup helper
- record success/failure without aborting the batch
- write per-ticket JSON artifacts, one summary JSON, and one Markdown report
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.\.venv\Scripts\python.exe -m pytest voc_agent/complaint_taxonomy_validator/tests/chain_test/test_live_chain_batch.py -q -s`
Expected: PASS even with some failed tickets, because failures are recorded rather than raised to abort the batch

### Task 4: Verify the complete chain batch validation flow

**Files:**
- Test: `voc_agent/complaint_taxonomy_validator/tests/test_response_parsing.py`
- Test: `voc_agent/complaint_taxonomy_validator/tests/chain_test/test_batch_runner.py`
- Test: `voc_agent/complaint_taxonomy_validator/tests/chain_test/test_live_chain_batch.py`

- [ ] **Step 1: Run focused unit tests**

Run: `.\.venv\Scripts\python.exe -m pytest voc_agent/complaint_taxonomy_validator/tests/test_response_parsing.py voc_agent/complaint_taxonomy_validator/tests/chain_test/test_batch_runner.py -q`
Expected: PASS

- [ ] **Step 2: Run the live 20-ticket batch validation**

Run: `.\.venv\Scripts\python.exe -m pytest voc_agent/complaint_taxonomy_validator/tests/chain_test/test_live_chain_batch.py -q -s`
Expected: PASS, with summary and Markdown report written under the chain test output directory

- [ ] **Step 3: Inspect the generated evidence**

Check:
- `voc_agent/complaint_taxonomy_validator/tests/chain_test/output/*.json`
- `voc_agent/complaint_taxonomy_validator/tests/chain_test/output/*.md`

Expected:
- per-ticket result files exist
- one summary JSON exists
- one Markdown report exists with success rate and main failure reasons
