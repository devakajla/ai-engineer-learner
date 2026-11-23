import threading

import pytest

from solution import run_all, try_all


def test_run_all_keeps_input_order():
    assert run_all(lambda x: x * 2, [1, 2, 3]) == [2, 4, 6], "results must follow the input order"


def test_run_all_empty():
    assert run_all(lambda x: x, []) == []


def test_run_all_uses_several_threads():
    barrier = threading.Barrier(3, timeout=5)

    def job(x):
        barrier.wait()          # only passes if 3 jobs run at the same time
        return x

    assert run_all(job, [1, 2, 3], max_workers=3) == [1, 2, 3], "jobs must run in parallel"


def test_run_all_bad_workers():
    with pytest.raises(ValueError):
        run_all(lambda x: x, [1], max_workers=0)


def test_try_all_success_and_failure_in_order():
    out = try_all(lambda x: 10 // x, [5, 0, 2])
    assert out[0] == (True, 2)
    assert out[1][0] is False and isinstance(out[1][1], ZeroDivisionError), "failed job -> (False, error)"
    assert out[2] == (True, 5), "a failure must not stop later jobs"


def test_try_all_all_fail():
    def boom(x):
        raise KeyError(x)

    out = try_all(boom, ["a", "b"])
    assert [ok for ok, _ in out] == [False, False]
    assert all(isinstance(err, KeyError) for _, err in out)


def test_try_all_bad_workers():
    with pytest.raises(ValueError):
        try_all(lambda x: x, [1], max_workers=-1)
