#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus, urlsplit, urlunsplit

REEXEC_ENV = "PROJECT_DB_EXECUTOR_REEXEC"
DEPENDENCY_ENV = "PROJECT_DB_EXECUTOR_DEPS_READY"
SCRIPT_PATH = str(Path(__file__).resolve())
PACKAGE_SPECS = [
    "SQLAlchemy>=2,<3",
    "python-dotenv>=1,<2",
    "sqlparse>=0.5,<1",
    "psycopg[binary]>=3,<4",
    "PyMySQL>=1,<2",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQL using the repository database configuration.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--sql", help="SQL text to execute")
    source.add_argument("--file", help="Path to a .sql file to execute")
    parser.add_argument("--env-file", help="Path to the env file. Defaults to <project-root>/.env")
    parser.add_argument("--project-root", help="Override project root detection")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of table output")
    parser.add_argument("--limit", type=int, default=50, help="Maximum rows to print per statement")
    parser.add_argument("--echo-sql", action="store_true", help="Print each statement before executing it")
    return parser.parse_args()


def find_project_root(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()

    current = Path.cwd().resolve()
    markers = (".env", "pyproject.toml", ".git")
    for candidate in [current, *current.parents]:
        if any((candidate / marker).exists() for marker in markers):
            return candidate
    return current


def local_python_candidates(project_root: Path, os_name: str | None = None) -> list[Path]:
    platform_os = os_name or os.name
    if platform_os == "nt":
        return [
            project_root / ".venv" / "Scripts" / "python.exe",
            project_root / "venv" / "Scripts" / "python.exe",
        ]

    return [
        project_root / ".venv" / "bin" / "python",
        project_root / "venv" / "bin" / "python",
    ]


def repo_looks_like_uv(project_root: Path) -> bool:
    if (project_root / "uv.lock").exists():
        return True
    pyproject = project_root / "pyproject.toml"
    if not pyproject.exists():
        return False
    try:
        content = pyproject.read_text(encoding="utf-8")
    except OSError:
        return False
    return "[project]" in content or "[tool.uv]" in content


def reexec_command(command: list[str], env: dict[str, str], project_root: Path, *, use_path: bool = False) -> None:
    if os.name == "nt":
        completed = subprocess.run(command, check=False, cwd=str(project_root), env=env)
        raise SystemExit(completed.returncode)

    executable = command[0]
    if use_path:
        os.execvpe(executable, command, env)
    else:
        os.execve(executable, command, env)


def maybe_reexec_into_project_python(project_root: Path) -> None:
    if os.environ.get(REEXEC_ENV) == "1":
        return

    current_python = Path(sys.executable).resolve()
    for candidate in local_python_candidates(project_root):
        if candidate.exists() and os.access(candidate, os.X_OK):
            if candidate.resolve() != current_python:
                env = os.environ.copy()
                env[REEXEC_ENV] = "1"
                reexec_command([str(candidate), SCRIPT_PATH, *sys.argv[1:]], env, project_root)
            return

    if repo_looks_like_uv(project_root) and shutil.which("uv"):
        env = os.environ.copy()
        env[REEXEC_ENV] = "1"
        reexec_command(["uv", "run", "python", SCRIPT_PATH, *sys.argv[1:]], env, project_root, use_path=True)


def ensure_dependencies(project_root: Path) -> None:
    if os.environ.get(DEPENDENCY_ENV) == "1":
        return

    required_modules = ("sqlalchemy", "dotenv", "sqlparse", "psycopg", "pymysql")
    missing = [name for name in required_modules if importlib.util.find_spec(name) is None]

    if not missing:
        return

    target_python = Path(sys.executable)
    for candidate in local_python_candidates(project_root):
        if candidate.exists() and os.access(candidate, os.X_OK):
            target_python = candidate
            break

    if shutil.which("uv"):
        cmd = ["uv", "pip", "install", "--python", str(target_python), *PACKAGE_SPECS]
    else:
        cmd = [str(target_python), "-m", "pip", "install", *PACKAGE_SPECS]

    subprocess.run(cmd, check=True, cwd=str(project_root))
    env = os.environ.copy()
    env[DEPENDENCY_ENV] = "1"
    reexec_command([str(target_python), SCRIPT_PATH, *sys.argv[1:]], env, project_root)


def load_runtime_modules() -> tuple[Any, Any, Any, Any]:
    from dotenv import dotenv_values
    from sqlalchemy import create_engine, text
    import sqlparse

    return dotenv_values, create_engine, text, sqlparse


def resolve_env_file(project_root: Path, env_file_arg: str | None) -> Path:
    if env_file_arg:
        return Path(env_file_arg).expanduser().resolve()
    return project_root / ".env"


def load_env_map(env_file: Path, dotenv_values: Any) -> dict[str, str]:
    if not env_file.exists():
        raise FileNotFoundError(f"Env file not found: {env_file}")
    values = dotenv_values(env_file)
    return {str(key): str(value) for key, value in values.items() if key and value is not None}


def first_present(env_map: dict[str, str], *keys: str) -> str | None:
    for key in keys:
        value = env_map.get(key)
        if value:
            return value.strip()
    return None


def normalize_url(raw_url: str) -> str:
    if raw_url.startswith("postgres://"):
        return "postgresql+psycopg://" + raw_url[len("postgres://"):]
    if raw_url.startswith("postgresql://"):
        return "postgresql+psycopg://" + raw_url[len("postgresql://"):]
    if raw_url.startswith("mysql://"):
        return "mysql+pymysql://" + raw_url[len("mysql://"):]
    return raw_url


def build_url_from_parts(env_map: dict[str, str]) -> str | None:
    dialect = first_present(env_map, "DB_DIALECT", "DB_ENGINE", "DB_TYPE", "DATABASE_TYPE") or "postgresql"
    dialect = dialect.strip().lower()

    if dialect in {"sqlite", "sqlite3"}:
        sqlite_path = first_present(env_map, "SQLITE_PATH", "DB_PATH", "DATABASE_PATH") or ":memory:"
        if sqlite_path == ":memory:":
            return "sqlite:///:memory:"
        return f"sqlite:///{Path(sqlite_path).expanduser().resolve()}"

    host = first_present(env_map, "DB_HOST", "DATABASE_HOST", "PGHOST", "MYSQL_HOST")
    port = first_present(env_map, "DB_PORT", "DATABASE_PORT", "PGPORT", "MYSQL_PORT")
    user = first_present(env_map, "DB_USER", "DB_USERNAME", "PGUSER", "MYSQL_USER")
    password = first_present(env_map, "DB_PASSWORD", "DB_PASS", "PGPASSWORD", "MYSQL_PASSWORD")
    database = first_present(env_map, "DB_NAME", "DB_DATABASE", "PGDATABASE", "MYSQL_DATABASE")

    if not all([host, user, database]):
        return None

    driver = {
        "postgres": "postgresql+psycopg",
        "postgresql": "postgresql+psycopg",
        "mysql": "mysql+pymysql",
        "mariadb": "mysql+pymysql",
    }.get(dialect, dialect)

    auth = quote_plus(user)
    if password:
        auth += f":{quote_plus(password)}"
    location = host
    if port:
        location += f":{port}"
    return f"{driver}://{auth}@{location}/{quote_plus(database)}"


def resolve_database_url(env_map: dict[str, str]) -> str:
    raw_url = first_present(
        env_map,
        "DATABASE_URL",
        "DATABASEURL",
        "DB_URL",
        "DB_DSN",
        "POSTGRES_URL",
        "POSTGRESQL_URL",
        "MYSQL_URL",
        "SQLITE_URL",
    )
    if raw_url:
        return normalize_url(raw_url)

    built = build_url_from_parts(env_map)
    if built:
        return built

    raise RuntimeError("No supported database connection config found in env file")


def redact_url(db_url: str) -> str:
    parts = urlsplit(db_url)
    hostname = parts.hostname or ""
    port = f":{parts.port}" if parts.port else ""
    username = parts.username or ""
    auth = username
    if username:
        auth += ":***"
        netloc = f"{auth}@{hostname}{port}"
    else:
        netloc = f"{hostname}{port}"
    return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))


def read_sql(args: argparse.Namespace) -> str:
    if args.sql:
        return args.sql
    file_path = Path(args.file).expanduser().resolve()
    return file_path.read_text(encoding="utf-8")


def split_statements(sql_text: str, sqlparse: Any) -> list[str]:
    statements = [item.strip() for item in sqlparse.split(sql_text) if item.strip()]
    if not statements:
        raise RuntimeError("No executable SQL statement found")
    return statements


def rows_to_dicts(result: Any, limit: int) -> tuple[list[dict[str, Any]], bool]:
    rows = result.mappings().fetchmany(limit + 1)
    truncated = len(rows) > limit
    rows = rows[:limit]
    return [dict(row) for row in rows], truncated


def render_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "(no rows)"

    columns = list(rows[0].keys())
    widths = {column: len(str(column)) for column in columns}
    for row in rows:
        for column in columns:
            widths[column] = max(widths[column], len(str(row.get(column, ""))))

    def format_row(row: dict[str, Any] | None, sep: str = " | ") -> str:
        source = row or {column: column for column in columns}
        return sep.join(str(source.get(column, column)).ljust(widths[column]) for column in columns)

    divider = "-+-".join("-" * widths[column] for column in columns)
    body = [format_row(row) for row in rows]
    return "\n".join([format_row(None), divider, *body])


def execute_statements(engine: Any, statements: list[str], text: Any, limit: int, echo_sql: bool) -> list[dict[str, Any]]:
    results = []
    with engine.begin() as connection:
        for index, statement in enumerate(statements, start=1):
            if echo_sql:
                print(f"-- statement {index} --\n{statement}\n", file=sys.stderr)
            result = connection.execute(text(statement))
            entry: dict[str, Any] = {
                "index": index,
                "statement": statement,
                "returns_rows": bool(result.returns_rows),
                "rowcount": result.rowcount,
            }
            if result.returns_rows:
                rows, truncated = rows_to_dicts(result, limit)
                entry["rows"] = rows
                entry["truncated"] = truncated
            results.append(entry)
    return results


def print_human_output(connection_label: str, results: list[dict[str, Any]]) -> None:
    print(f"Connection: {connection_label}")
    for entry in results:
        print(f"\nStatement {entry['index']}:")
        if entry["returns_rows"]:
            print(render_table(entry.get("rows", [])))
            if entry.get("truncated"):
                print("... output truncated; raise --limit to see more rows")
        else:
            print(f"OK, rowcount={entry['rowcount']}")


def main() -> int:
    args = parse_args()
    project_root = find_project_root(args.project_root)
    maybe_reexec_into_project_python(project_root)
    ensure_dependencies(project_root)

    dotenv_values, create_engine, text, sqlparse = load_runtime_modules()
    env_file = resolve_env_file(project_root, args.env_file)
    env_map = load_env_map(env_file, dotenv_values)
    database_url = resolve_database_url(env_map)
    sql_text = read_sql(args)
    statements = split_statements(sql_text, sqlparse)

    engine = create_engine(database_url, future=True)
    results = execute_statements(engine, statements, text, args.limit, args.echo_sql)
    connection_label = redact_url(database_url)

    if args.json:
        print(json.dumps({"connection": connection_label, "results": results}, ensure_ascii=False, indent=2, default=str))
    else:
        print_human_output(connection_label, results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
