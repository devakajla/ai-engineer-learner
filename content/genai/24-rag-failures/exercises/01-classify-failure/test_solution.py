from solution import classify_failure


def test_retrieval_miss():
    assert classify_failure(["c3"], ["c1", "c2"], False) == "retrieval_miss"
    assert classify_failure(["c3"], [], True) == "retrieval_miss", "no chunk found means a miss, even if the answer looked fine"


def test_generation_miss():
    assert classify_failure(["c3"], ["c3", "c9"], False) == "generation_miss"


def test_ok():
    assert classify_failure(["c3", "c4"], ["c4"], True) == "ok"


def test_unanswerable():
    assert classify_failure([], ["c1"], True) == "ok"
    assert classify_failure([], ["c1"], False) == "hallucination"
