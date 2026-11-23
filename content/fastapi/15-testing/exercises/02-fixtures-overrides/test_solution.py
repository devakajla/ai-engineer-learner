import inspect
import os
import subprocess
import sys

import pytest

MUTANTS = ["create_status", "pinned_first", "patch_overwrites", "delete_noop"]


def run_suite(mutant=""):
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "solution.py"],
        env={**os.environ, "MUTANT": mutant}, capture_output=True, text=True, timeout=60,
    )


def test_passes_on_correct_app():
    r = run_suite()
    assert r.returncode == 0, "your tests must pass on the correct app:\n" + r.stdout[-2000:]


def test_uses_override_fixture():
    import solution

    src = inspect.getsource(solution)
    assert "dependency_overrides" in src, "override get_repo in a fixture"
    assert "def client" in src and "yield" in src, "write a yield fixture called client"
    assert ".clear()" in src or ".pop(" in src, "remove the override after each test"


@pytest.mark.parametrize("mutant", MUTANTS)
def test_catches_bug(mutant):
    assert run_suite(mutant).returncode != 0, f"your tests did not catch the '{mutant}' bug"
