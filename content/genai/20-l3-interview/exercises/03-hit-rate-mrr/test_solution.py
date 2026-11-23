import pytest

from solution import retrieval_metrics

RUNS = [(["a", "b", "c"], "b"), (["x", "y", "z"], "q"), (["m", "n"], "m")]


def test_examples():
    result = retrieval_metrics(RUNS, 3)
    assert result["hit_rate"] == pytest.approx(2 / 3) and result["mrr"] == pytest.approx(0.5)
    result = retrieval_metrics(RUNS, 1)
    assert result["hit_rate"] == pytest.approx(1 / 3) and result["mrr"] == pytest.approx(1 / 3)
    assert retrieval_metrics([], 3) == {"hit_rate": 0.0, "mrr": 0.0}


def test_rank_beyond_k_does_not_count():
    runs = [(["a", "b", "c", "d"], "d")]
    assert retrieval_metrics(runs, 3) == {"hit_rate": 0.0, "mrr": 0.0}
    assert retrieval_metrics(runs, 4) == {"hit_rate": 1.0, "mrr": 0.25}


def test_all_found_first():
    runs = [(["a"], "a"), (["b", "c"], "b")]
    assert retrieval_metrics(runs, 5) == {"hit_rate": 1.0, "mrr": 1.0}


def test_empty_results_and_floats():
    result = retrieval_metrics([([], "a")], 3)
    assert result == {"hit_rate": 0.0, "mrr": 0.0}
    assert all(type(v) is float for v in retrieval_metrics(RUNS, 2).values())


def test_bad_k():
    for k in (0, -1):
        with pytest.raises(ValueError):
            retrieval_metrics(RUNS, k)
