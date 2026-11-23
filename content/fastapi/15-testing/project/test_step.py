"""Step 15 checks: runs the learner's OWN test suite, then mutation-tests it."""

import ast
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path.cwd()

MUTANT_PLUGIN = textwrap.dedent(
    '''
    import os

    MUTANT = os.environ.get("TASKFLOW_MUTANT", "")


    def pytest_configure(config):
        from app.services import task_service as ts

        Service = ts.TaskService
        if MUTANT == "create_ignores_priority":
            original = Service.create

            async def create(self, data):
                return await original(self, data.model_copy(update={"priority": "medium"}))

            Service.create = create
        elif MUTANT == "update_noop":
            async def update(self, task_id, data):
                return await self.get(task_id)

            Service.update = update
        elif MUTANT == "delete_noop":
            async def delete(self, task_id):
                await self.get(task_id)

            Service.delete = delete
        elif MUTANT == "done_filter_ignored":
            original_list = Service.list

            async def list_(self, **kwargs):
                kwargs["done"] = None
                return await original_list(self, **kwargs)

            Service.list = list_
    '''
)


def count_tests() -> int:
    total = 0
    for path in (ROOT / "tests").glob("test_*.py"):
        tree = ast.parse(path.read_text())
        total += sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
        )
    return total


def run_suite(tmp_path, mutant: str = "") -> subprocess.CompletedProcess:
    plugin_dir = tmp_path / "plugin"
    plugin_dir.mkdir(exist_ok=True)
    (plugin_dir / "_taskflow_mutants.py").write_text(MUTANT_PLUGIN)
    env = {
        **os.environ,
        "TASKFLOW_MUTANT": mutant,
        "DATABASE_URL": f"sqlite+aiosqlite:///{tmp_path / 'must_not_be_used.db'}",
        "PYTHONPATH": os.pathsep.join([str(plugin_dir), str(ROOT), os.environ.get("PYTHONPATH", "")]),
    }
    return subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider", "-p", "_taskflow_mutants", "-x"],
        cwd=ROOT, env=env, capture_output=True, text=True, timeout=180,
    )


def test_structure():
    assert (ROOT / "tests" / "conftest.py").exists(), "create tests/conftest.py"
    conftest = (ROOT / "tests" / "conftest.py").read_text()
    assert "dependency_overrides" in conftest, "override get_db in a fixture in conftest.py"
    assert count_tests() >= 10, f"write at least 10 test functions (found {count_tests()})"


def test_suite_passes_and_is_isolated(tmp_path):
    r = run_suite(tmp_path)
    assert r.returncode == 0, "your test suite must pass:\n" + (r.stdout + r.stderr)[-3000:]
    assert not (tmp_path / "must_not_be_used.db").exists(), "tests used the app's real database — override get_db"


@pytest.mark.parametrize("mutant", ["create_ignores_priority", "update_noop", "delete_noop", "done_filter_ignored"])
def test_suite_catches_bug(tmp_path, mutant):
    r = run_suite(tmp_path, mutant)
    assert r.returncode != 0, f"your suite still passes when '{mutant}' is broken — add or strengthen a test"
