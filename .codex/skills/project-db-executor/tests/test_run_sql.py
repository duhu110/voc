from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_sql.py"
SPEC = importlib.util.spec_from_file_location("project_db_executor_run_sql", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load run_sql.py from {SCRIPT_PATH}")

run_sql = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(run_sql)


class LocalPythonCandidatesTest(unittest.TestCase):
    def test_windows_virtualenv_candidates_are_discovered(self) -> None:
        project_root = Path("C:/workspace/voc")

        candidates = run_sql.local_python_candidates(project_root, os_name="nt")

        self.assertEqual(
            candidates,
            [
                project_root / ".venv" / "Scripts" / "python.exe",
                project_root / "venv" / "Scripts" / "python.exe",
            ],
        )

    def test_posix_virtualenv_candidates_are_discovered(self) -> None:
        project_root = Path("/workspace/voc")

        candidates = run_sql.local_python_candidates(project_root, os_name="posix")

        self.assertEqual(
            candidates,
            [
                project_root / ".venv" / "bin" / "python",
                project_root / "venv" / "bin" / "python",
            ],
        )


class ReexecIntoProjectPythonTest(unittest.TestCase):
    @patch.object(run_sql.subprocess, "run")
    @patch.object(run_sql.os, "execve")
    @patch.object(run_sql.os, "environ", {}, create=True)
    def test_windows_reexec_uses_subprocess(self, mock_execve, mock_run) -> None:
        env = {"PATH": "C:/Windows/System32"}
        project_root = Path("C:/workspace/voc")

        with patch.object(run_sql.os, "name", "nt"), patch.object(
            run_sql.os, "access", return_value=True
        ), patch.object(
            run_sql.Path, "exists", return_value=True
        ), patch.object(
            run_sql.Path, "cwd", return_value=Path("C:/workspace/voc")
        ), patch.object(
            run_sql.sys, "argv", ["run_sql.py", "--sql", "select 1"]
        ), patch.object(
            run_sql.sys, "executable", "C:/Python311/python.exe"
        ), patch.object(
            run_sql.os, "execve"
        ) as mock_execve_call, patch.object(
            run_sql.os, "environ", env, create=True
        ):
            with self.assertRaises(SystemExit) as exc:
                run_sql.maybe_reexec_into_project_python(Path("C:/workspace/voc"))

        mock_run.assert_called_once_with(
            [
                str(project_root / ".venv" / "Scripts" / "python.exe"),
                str(SCRIPT_PATH),
                "--sql",
                "select 1",
            ],
            check=False,
            cwd=str(project_root),
            env={"PATH": "C:/Windows/System32", run_sql.REEXEC_ENV: "1"},
        )
        self.assertEqual(exc.exception.code, mock_run.return_value.returncode)
        mock_execve.assert_not_called()
        mock_execve_call.assert_not_called()


if __name__ == "__main__":
    unittest.main()
