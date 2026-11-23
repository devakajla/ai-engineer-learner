from solution import failure_report

RESULTS = [
    {"question": "q1", "expected": ["a"], "retrieved": ["a"], "answer_ok": True},
    {"question": "q2", "expected": ["b"], "retrieved": ["x"], "answer_ok": False},
    {"question": "q3", "expected": ["c"], "retrieved": ["c"], "answer_ok": False},
    {"question": "q4", "expected": [], "retrieved": ["x"], "answer_ok": False},
    {"question": "q5", "expected": ["b"], "retrieved": [], "answer_ok": False},
]


def test_counts():
    out = failure_report(RESULTS)
    assert out["counts"] == {"ok": 1, "retrieval_miss": 2, "generation_miss": 1, "hallucination": 1}


def test_by_category_order():
    out = failure_report(RESULTS)
    assert out["by_category"]["retrieval_miss"] == ["q2", "q5"]
    assert out["by_category"]["ok"] == ["q1"]


def test_empty_has_all_keys():
    out = failure_report([])
    assert out["counts"] == {"ok": 0, "retrieval_miss": 0, "generation_miss": 0, "hallucination": 0}
    assert out["by_category"] == {"ok": [], "retrieval_miss": [], "generation_miss": [], "hallucination": []}
