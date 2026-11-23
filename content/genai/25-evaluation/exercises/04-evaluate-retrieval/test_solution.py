from solution import evaluate_retrieval

TABLE = {
    "q1": ["a", "x", "y"],
    "q2": ["x", "y", "z"],
    "q3": ["m", "b", "n"],
}


def retrieve(question, k):
    return [{"id": i} for i in TABLE[question][:k]]


CASES = [
    {"question": "q1", "expected": ["a"]},
    {"question": "q2", "expected": ["b"]},
    {"question": "q3", "expected": ["b"]},
]


def test_scores():
    out = evaluate_retrieval(retrieve, CASES, k=3)
    assert out["n"] == 3
    assert out["recall"] == round(2 / 3, 4)
    assert out["precision"] == round((1 / 3 + 0 + 1 / 3) / 3, 4)
    assert out["mrr"] == round((1 + 0 + 0.5) / 3, 4)
    assert out["misses"] == ["q2"]


def test_k_changes_result():
    out = evaluate_retrieval(retrieve, CASES, k=1)
    assert out["recall"] == round(1 / 3, 4)
    assert out["misses"] == ["q2", "q3"]


def test_retrieve_gets_k():
    seen = []

    def spy(question, k):
        seen.append(k)
        return []

    evaluate_retrieval(spy, CASES, k=4)
    assert seen == [4, 4, 4]


def test_unanswerable_case_is_not_a_miss():
    out = evaluate_retrieval(retrieve, [{"question": "q1", "expected": []}], k=3)
    assert out["misses"] == []
    assert out["recall"] == 1.0


def test_empty():
    assert evaluate_retrieval(retrieve, []) == {"n": 0, "recall": 0.0, "precision": 0.0, "mrr": 0.0, "misses": []}
