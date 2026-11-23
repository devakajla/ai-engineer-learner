from solution import filter_hits

HITS = [
    {"id": "a", "tenant": "acme"},
    {"id": "b", "tenant": "other"},
    {"id": "c", "tenant": "acme", "groups": ["hr"]},
    {"id": "d", "tenant": "acme", "groups": ["dev", "hr"]},
]


def test_filter():
    out = filter_hits(HITS, {"tenant": "acme", "groups": ["dev"]})
    assert [h["id"] for h in out] == ["a", "d"]


def test_hr():
    out = filter_hits(HITS, {"tenant": "acme", "groups": ["hr"]})
    assert [h["id"] for h in out] == ["a", "c", "d"]


def test_nobody():
    assert filter_hits(HITS, {"tenant": "none"}) == []
    assert filter_hits([], {"tenant": "acme"}) == []


def test_input_not_changed():
    before = list(HITS)
    filter_hits(HITS, {"tenant": "acme"})
    assert HITS == before
