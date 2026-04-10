---
name: project-db-executor
description: Execute and inspect this repository's database through Python with project-local environment detection, automatic dependency bootstrap, and connection loading from the repository root .env. Use when Codex needs to run SQL, inspect schema, validate migrations, execute a .sql file, or troubleshoot this project's database using the repo's own .venv, venv, or uv setup.
---

# Project DB Executor

Use this skill to run SQL for this repository through the bundled Python runner instead of rewriting database connection code.

## Workflow

1. Start from the repository root.
2. Read the root `.env` only to discover the database connection.
3. Run [`scripts/run_sql.py`](/Users/duhu/code/voc/.codex/skills/project-db-executor/scripts/run_sql.py) for all database access.
4. Prefer read-only inspection first. Use write statements only when the user explicitly asks.

## Runner Rules

- Let the script choose the interpreter. It re-execs into `.venv/bin/python` or `venv/bin/python` when present.
- If no local virtual environment exists but the repo looks like a uv project, let the script re-exec through `uv run python`.
- Let the script install its required Python packages into the project environment when they are missing.
- Do not hardcode credentials in commands or patches. The runner reads them from the repository root `.env`.

## Commands

Run inline SQL:

```bash
python .codex/skills/project-db-executor/scripts/run_sql.py --sql "SELECT 1"
```

Run a SQL file:

```bash
python .codex/skills/project-db-executor/scripts/run_sql.py --file sql_scripts/数据库结构巡检\ SQL.sql
```

Return JSON:

```bash
python .codex/skills/project-db-executor/scripts/run_sql.py --sql "SELECT current_database()" --json
```

Use a different env file temporarily:

```bash
python .codex/skills/project-db-executor/scripts/run_sql.py --sql "SELECT 1" --env-file .env.local
```

## Connection Discovery

The runner first looks for URL-style variables, then falls back to component-style variables. It already supports this repository's current `DATABASEURL` key.

Read [`references/connection-conventions.md`](/Users/duhu/code/voc/.codex/skills/project-db-executor/references/connection-conventions.md) when the connection format needs to be extended.

## Output Rules

- Default to human-readable table output.
- Use `--json` when another tool or script needs structured output.
- For multi-statement SQL files, expect one result block per statement.
- Default row preview is limited. Raise `--limit` only when the user actually needs more rows.
