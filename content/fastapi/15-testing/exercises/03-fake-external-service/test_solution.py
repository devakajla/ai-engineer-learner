import os
import subprocess
import sys

import pytest

MUTANTS = ["timeout_500", "unknown_city", "advice_threshold", "temp_rounding"]


def run_suite(mutant=""):
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "solution.py"],
        env={**os.environ, "MUTANT": mutant}, capture_output=True, text=True, timeout=60,
    )


def test_passes_on_correct_app():
    r = run_suite()
    assert r.returncode == 0, "your tests must pass on the correct app (and never call the real client):\n" + r.stdout[-2000:]


@pytest.mark.parametrize("mutant", MUTANTS)
def test_catches_bug(mutant):
    assert run_suite(mutant).returncode != 0, f"your tests did not catch the '{mutant}' bug"
