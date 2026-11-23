from solution import post_filter

RESULTS = [
    {"id": "a", "metadata": {"source": "tasks.md", "lang": "en"}},
    {"id": "b", "metadata": {"source": "auth.md", "lang": "en"}},
    {"id": "c", "metadata": {"source": "auth.md", "lang": "hi"}},
]


def ids(results):
    return [r["id"] for r in results]


def test_examples():
    assert ids(post_filter(RESULTS, {"source": "auth.md"}, 5)) == ["b", "c"]
    assert ids(post_filter(RESULTS, {"source": "auth.md", "lang": "hi"}, 5)) == ["c"]
    assert ids(post_filter(RESULTS, {}, 2)) == ["a", "b"]


def test_k_limits_and_edges():
    assert ids(post_filter(RESULTS, {"source": "auth.md"}, 1)) == ["b"]
    assert post_filter(RESULTS, {}, 0) == []
    assert post_filter(RESULTS, {}, -3) == []
    assert post_filter([], {"source": "x"}, 3) == []


def test_missing_key_and_wrong_value():
    assert post_filter(RESULTS, {"version": 2}, 5) == [], "no result has a version key"
    assert post_filter(RESULTS, {"source": "nope.md"}, 5) == []
    odd = [{"id": "z", "metadata": {}}]
    assert post_filter(odd, {"source": "a"}, 5) == []
    assert ids(post_filter(odd, {}, 5)) == ["z"]


def test_falsy_values_are_real_values():
    items = [{"id": "p", "metadata": {"heading": ""}}, {"id": "q", "metadata": {"heading": "X"}}]
    assert ids(post_filter(items, {"heading": ""}, 5)) == ["p"], "an empty string is a value, not 'no filter'"


def test_input_is_not_changed():
    before = [dict(r) for r in RESULTS]
    post_filter(RESULTS, {"source": "auth.md"}, 1)
    assert RESULTS == before
