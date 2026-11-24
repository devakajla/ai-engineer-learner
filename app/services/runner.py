"""Runs hidden tests against the learner's code.

- Exercises: the code is written as solution.py into a fresh temp dir next to
  test_solution.py (plus any helper files from the exercise folder).
- Project checkpoints: a lesson's test_step.py runs against the learner's real
  project folder, inside that project's own environment (`uv run --project`).

pytest runs in a subprocess with a timeout. This is a single-user local app, so
there is no heavier sandbox.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import shutil
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

from app.config import PROJECT_TEST_TIMEOUT_SECONDS, TEST_TIMEOUT_SECONDS

# Files in an exercise folder that must never be copied next to the learner's code.
_PRIVATE = {"solution.py", "starter.py", "prompt.md"}

_PYTEST_ARGS = [
    "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider", "-p", "report_plugin",
    "--tb=short", "-W", "ignore::DeprecationWarning",
]  # fmt: skip

_PLUGIN_DIR = str(Path(__file__).parent)  # holds report_plugin.py


@dataclass
class RunResult:
    passed: bool
    summary: str
    output: str
    seconds: float
    timed_out: bool = False
    failures: list[dict] = field(default_factory=list)


async def _run(cmd: list[str], cwd: Path, timeout: float, hide: str | None = None) -> RunResult:
    start = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="learner-report-") as report_dir:
        report = Path(report_dir) / "report.json"
        env = {
            **os.environ,
            "PYTHONDONTWRITEBYTECODE": "1",
            "LEARNER_REPORT": str(report),
            "PYTHONPATH": os.pathsep.join(filter(None, [_PLUGIN_DIR, os.environ.get("PYTHONPATH")])),
        }
        env.pop("VIRTUAL_ENV", None)  # don't leak the Learner venv into `uv run --project`
        return await _run_with_env(cmd, cwd, timeout, hide, env, report, start)


def _read_failures(report: Path) -> list[dict]:
    try:
        return json.loads(report.read_text())
    except (OSError, ValueError):
        return []  # plugin did not run: the UI falls back to the raw output


async def _run_with_env(
    cmd: list[str], cwd: Path, timeout: float, hide: str | None, env: dict, report: Path, start: float
) -> RunResult:
    proc = await asyncio.create_subprocess_exec(
        *cmd, cwd=cwd, env=env, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
    )
    try:
        out, _ = await asyncio.wait_for(proc.communicate(), timeout)
    except TimeoutError:
        proc.kill()
        await proc.wait()
        return RunResult(False, f"Timed out after {timeout:.0f}s (infinite loop?)", "", timeout, timed_out=True)
    text = out.decode(errors="replace")
    if hide:
        text = text.replace(hide, "<tests>")
    return RunResult(
        proc.returncode == 0, _summary(text, proc.returncode), text, time.perf_counter() - start,
        failures=_read_failures(report),
    )  # fmt: skip


async def run_tests(code: str, exercise_dir: Path, timeout: float = TEST_TIMEOUT_SECONDS) -> RunResult:
    with tempfile.TemporaryDirectory(prefix="learner-") as tmp:
        tmp_path = Path(tmp)
        for f in exercise_dir.iterdir():
            if f.is_file() and f.name not in _PRIVATE:
                shutil.copy(f, tmp_path / f.name)
        (tmp_path / "solution.py").write_text(code)
        return await _run([sys.executable, *_PYTEST_ARGS, "test_solution.py"], tmp_path, timeout, hide=tmp)


@dataclass
class ScriptResult:
    stdout: str
    stderr: str
    seconds: float
    timed_out: bool = False


_MAX_OUTPUT_CHARS = 20_000


def _cap(text: str) -> str:
    if len(text) <= _MAX_OUTPUT_CHARS:
        return text
    return text[:_MAX_OUTPUT_CHARS] + "\n... (output cut)"


async def run_script(code: str, timeout: float = TEST_TIMEOUT_SECONDS) -> ScriptResult:
    """Run free code once (the trial room). No tests: just show what it prints.

    stdin is closed, so `input()` raises EOFError at once instead of hanging.
    """
    with tempfile.TemporaryDirectory(prefix="learner-trial-") as tmp:
        (Path(tmp) / "main.py").write_text(code)
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUNBUFFERED": "1"}
        env.pop("VIRTUAL_ENV", None)
        start = time.perf_counter()
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-I", "main.py", cwd=tmp, env=env,
            stdin=asyncio.subprocess.DEVNULL, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )  # fmt: skip
        try:
            out, err = await asyncio.wait_for(proc.communicate(), timeout)
        except TimeoutError:
            proc.kill()
            await proc.wait()
            return ScriptResult("", f"Timed out after {timeout:.0f}s (infinite loop?)", timeout, timed_out=True)
        seconds = time.perf_counter() - start
        stderr = err.decode(errors="replace").replace(tmp, "<trial>")
        return ScriptResult(_cap(out.decode(errors="replace")), _cap(stderr), seconds)


def _uv() -> str | None:
    return shutil.which("uv") or next(
        (p for p in [str(Path.home() / ".local/bin/uv"), "/opt/homebrew/bin/uv"] if Path(p).exists()), None
    )


async def run_project_tests(
    project_dir: Path, test_file: Path, timeout: float = PROJECT_TEST_TIMEOUT_SECONDS, use_uv: bool = True
) -> RunResult:
    """Run one checkpoint test file against a project folder.

    The test file is copied to a temp dir (so no Learner config leaks in) and pytest
    runs with cwd = project_dir, so `from app.main import app` imports the learner's app.
    With use_uv=False it uses this interpreter instead (the content validator does that).
    """
    if not project_dir.is_dir():
        return RunResult(False, f"Folder not found: {project_dir}", "Create the folder first (see the step).", 0)
    with tempfile.TemporaryDirectory(prefix="learner-step-") as tmp:
        test_copy = Path(tmp) / "test_step.py"
        shutil.copy(test_file, test_copy)
        pytest_cmd = [*_PYTEST_ARGS, "--rootdir", tmp, str(test_copy)]
        if use_uv and (project_dir / "pyproject.toml").exists():
            uv = _uv()
            if not uv:
                return RunResult(False, "`uv` not found on PATH", "Install uv: https://docs.astral.sh/uv/", 0)
            cmd = [uv, "run", "--quiet", "--project", str(project_dir), "--with", "pytest", "--with", "httpx", "python", *pytest_cmd]
        else:
            cmd = [sys.executable, *pytest_cmd]
        return await _run(cmd, project_dir, timeout, hide=tmp)


def _summary(output: str, code: int | None) -> str:
    lines = [ln.strip("= ") for ln in output.strip().splitlines() if re.search(r"\b(passed|failed|error)", ln)]
    if lines:
        return lines[-1]
    return "All tests passed" if code == 0 else "Tests could not run (see output)"
