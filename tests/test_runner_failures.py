import asyncio
from pathlib import Path

from app.services.runner import run_tests



def _run(tmp_path, code):
    (tmp_path / "test_solution.py").write_text(
        "from solution import f\n\ndef test_f():\n    assert f(2) == 4, 'f(2) should be 4'\n"
    )
    return asyncio.run(run_tests(code, tmp_path))


def test_wrong_answer(tmp_path):
    r = _run(tmp_path, "def f(x):\n    return x + 1\n")
    (fail,) = r.failures
    assert fail["kind"] == "assertion" and fail["got"] == "3" and fail["expected"] == "4"
    assert "f(2) should be 4" in fail["message"]


def test_crash_points_at_learner_line(tmp_path):
    r = _run(tmp_path, "def f(x):\n    return x / 0\n")
    (fail,) = r.failures
    assert fail["exc_type"] == "ZeroDivisionError" and fail["line"] == 2 and "x / 0" in fail["source"]


def test_syntax_error(tmp_path):
    r = _run(tmp_path, "def f(x)\n    return x\n")
    assert r.failures[0]["kind"] == "syntax" and r.failures[0]["line"] == 1
