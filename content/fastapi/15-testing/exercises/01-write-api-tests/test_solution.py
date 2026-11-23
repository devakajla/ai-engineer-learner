import os
import subprocess
import sys

import pytest

MUTANTS = ["coupon_rate", "bulk_threshold", "unknown_coupon", "rounding", "qty"]


def run_suite(mutant=""):
    env = {**os.environ, "MUTANT": mutant}
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "solution.py"],
        env=env, capture_output=True, text=True, timeout=60,
    )


def test_suite_passes_on_correct_app():
    r = run_suite()
    assert r.returncode == 0, "your tests must pass on the correct app:\n" + r.stdout[-2000:]
    assert " passed" in r.stdout


def test_has_enough_tests():
    r = run_suite()
    passed = int(r.stdout.strip().splitlines()[-1].split(" passed")[0].split()[-1])
    assert passed >= 5, "write at least 5 test cases"


@pytest.mark.parametrize("mutant", MUTANTS)
def test_suite_catches_bug(mutant):
    r = run_suite(mutant)
    assert r.returncode != 0, f"your tests did not catch the '{mutant}' bug — add a test for that rule"
