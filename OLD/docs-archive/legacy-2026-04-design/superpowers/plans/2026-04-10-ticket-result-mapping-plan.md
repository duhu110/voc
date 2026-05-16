# Ticket Result Mapping And Schema Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align complaint ticket schemas and add code-to-ID resolvers so validator output can be transformed into database-ready result rows.

**Architecture:** Apply the database schema changes first so source and result tables use consistent `ticket_id` semantics and a simplified raw ticket processing flag. Then add shared lookup helpers in `voc_agent/share/tools` and verify them with focused unit tests before re-assessing write-readiness against the database design.

**Tech Stack:** PostgreSQL, SQLAlchemy, pytest, project-local SQL runner

---

### Task 1: Add lookup helper tests

**Files:**
- Create: `D:/project/FullStack/voc/voc_agent/share/tests/test_result_lookup.py`

- [ ] **Step 1: Write the failing tests**

```python
from voc_agent.share.tools.result_lookup import build_category_lookup, build_tag_lookup


def test_build_category_lookup_indexes_by_code():
    categories = [
        {'id': 11, 'code': 'RULE_PROCESS', 'name': '办理规则争议'},
        {'id': 12, 'code': 'FEE_PACKAGE', 'name': '套餐收费争议'},
    ]

    lookup = build_category_lookup(categories)

    assert lookup['RULE_PROCESS']['id'] == 11
    assert lookup['FEE_PACKAGE']['name'] == '套餐收费争议'


def test_build_tag_lookup_indexes_by_group_and_code():
    tags = [
        {'id': 21, 'group_code': 'PRODUCT', 'code': 'MOBILE', 'name': '移动业务'},
        {'id': 22, 'group_code': 'REQUEST', 'code': 'REFUND', 'name': '退费'},
    ]

    lookup = build_tag_lookup(tags)

    assert lookup[('PRODUCT', 'MOBILE')]['id'] == 21
    assert lookup[('REQUEST', 'REFUND')]['name'] == '退费'
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./.venv/Scripts/python.exe -m pytest voc_agent/share/tests/test_result_lookup.py -q`
Expected: FAIL with `ModuleNotFoundError` or missing helper symbol.

- [ ] **Step 3: Write minimal implementation**

Create a new `voc_agent/share/tools/result_lookup.py` module with:

```python
from __future__ import annotations

from typing import Any


def build_category_lookup(categories: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(item['code']): item for item in categories if item.get('code')}


def build_tag_lookup(tags: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (str(item['group_code']), str(item['code'])): item
        for item in tags
        if item.get('group_code') and item.get('code')
    }
```

Export both helpers from `voc_agent/share/tools/__init__.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `./.venv/Scripts/python.exe -m pytest voc_agent/share/tests/test_result_lookup.py -q`
Expected: PASS

### Task 2: Surface IDs in enabled category/tag fetchers

**Files:**
- Modify: `D:/project/FullStack/voc/voc_agent/share/tools/fetch_enabled_categories.py`
- Modify: `D:/project/FullStack/voc/voc_agent/share/tools/fetch_enabled_tags.py`
- Modify: `D:/project/FullStack/voc/voc_agent/complaint_taxonomy_validator/tests/test_result_normalizer.py`

- [ ] **Step 1: Write the failing test**

Add a test that passes category/tag metadata containing IDs into `normalize_result()` and asserts the normalized result still validates while preserving lookup-ready metadata in the source lists.

- [ ] **Step 2: Run test to verify it fails**

Run: `./.venv/Scripts/python.exe -m pytest voc_agent/complaint_taxonomy_validator/tests/test_result_normalizer.py -q`
Expected: FAIL because fetched metadata shape does not include IDs in the test fixture or lookup assumptions break.

- [ ] **Step 3: Write minimal implementation**

Update the SQL queries to select `id` from `complaint_category` and `complaint_tag`, keeping existing fields unchanged.

- [ ] **Step 4: Run test to verify it passes**

Run: `./.venv/Scripts/python.exe -m pytest voc_agent/complaint_taxonomy_validator/tests/test_result_normalizer.py -q`
Expected: PASS

### Task 3: Apply schema migration and document it

**Files:**
- Modify: `D:/project/FullStack/voc/docs/db_design.md`
- Modify: `D:/project/FullStack/voc/docs/project_steps.md`

- [ ] **Step 1: Inspect current database schema with the project DB executor**

Run: `python .codex/skills/project-db-executor/scripts/run_sql.py --sql "select column_name, data_type from information_schema.columns where table_name in ('raw_complaint_tickets','complaint_ticket_category_result','complaint_ticket_tag_result','complaint_ticket_keyword_result','complaint_ticket_match_detail') order by table_name, ordinal_position"`
Expected: current columns and `ticket_id` data types are visible before migration.

- [ ] **Step 2: Apply the migration with the project DB executor**

Run a SQL batch that:
- Drops `raw_complaint_tickets.process_status`, `error_message`, `emotion_level`, `core_appeal_category`, `escalation_risk`, `is_shirking`, `ai_features`
- Adds `raw_complaint_tickets.process_status boolean not null default false`
- Alters `ticket_id` in the four result tables from `bigint` to `varchar(100)` using `using ticket_id::varchar(100)`

- [ ] **Step 3: Update the design docs**

Reflect the raw table field removal/addition and the `ticket_id varchar(100)` change in `docs/db_design.md`, and note the simplified processing status behavior in `docs/project_steps.md` where relevant.

- [ ] **Step 4: Re-inspect the schema to verify it passes**

Run: `python .codex/skills/project-db-executor/scripts/run_sql.py --sql "select table_name, column_name, data_type from information_schema.columns where table_name in ('raw_complaint_tickets','complaint_ticket_category_result','complaint_ticket_tag_result','complaint_ticket_keyword_result','complaint_ticket_match_detail') and column_name in ('ticket_id','process_status','error_message','emotion_level','core_appeal_category','escalation_risk','is_shirking','ai_features') order by table_name, column_name"`
Expected: only the new boolean `process_status` remains on the raw table and all result-table `ticket_id` columns are `character varying`.

### Task 4: Re-assess DB write readiness

**Files:**
- No code changes required unless gaps are discovered during assessment.

- [ ] **Step 1: Re-run focused test suite**

Run: `./.venv/Scripts/python.exe -m pytest voc_agent/share/tests/test_result_lookup.py voc_agent/complaint_taxonomy_validator/tests/test_result_normalizer.py voc_agent/complaint_taxonomy_validator/tests/test_response_parsing.py -q`
Expected: PASS

- [ ] **Step 2: Re-check live chain output sample**

Run: `Get-Content D:/project/FullStack/voc/voc_agent/complaint_taxonomy_validator/tests/chain_test/output/summary__2026-04-10T15-11-39.json`
Expected: Use current output shape to compare with DB result, detail, and stats table requirements.

- [ ] **Step 3: Produce a gap assessment**

List which tables can now be filled directly, which still need a write adapter or aggregation layer, and why.
