from solution import prepare_context


def hits(n):
    return [{"id": i, "text": f"text {i}", "source": f"s{i}"} for i in range(n)]


def ids(hs):
    return [h["id"] for h in hs]


def test_five():
    assert ids(prepare_context(hits(5), 5)) == [0, 2, 4, 3, 1]


def test_four_and_two():
    assert ids(prepare_context(hits(4), 4)) == [0, 2, 3, 1]
    assert ids(prepare_context(hits(2), 2)) == [0, 1]


def test_max_hits_cuts_first():
    assert ids(prepare_context(hits(6), 3)) == [0, 2, 1]


def test_dedupe_applied():
    hs = [
        {"id": 0, "text": "same", "source": "a"},
        {"id": 1, "text": "SAME", "source": "b"},
        {"id": 2, "text": "other", "source": "c"},
    ]
    assert ids(prepare_context(hs, 5)) == [0, 2]


def test_max_per_source():
    hs = [{"id": i, "text": f"t{i}", "source": "same"} for i in range(4)]
    assert ids(prepare_context(hs, 5, max_per_source=2)) == [0, 1]


def test_zero_and_empty():
    assert prepare_context(hits(3), 0) == []
    assert prepare_context([], 3) == []
