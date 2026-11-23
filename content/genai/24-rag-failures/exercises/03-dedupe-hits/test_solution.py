from solution import dedupe_hits

HITS = [
    {"id": 1, "text": "Use DELETE.", "source": "a.md"},
    {"id": 2, "text": "use   delete.", "source": "b.md"},
    {"id": 3, "text": "Other.", "source": "a.md"},
    {"id": 4, "text": "Third.", "source": "a.md"},
]


def ids(hits):
    return [h["id"] for h in hits]


def test_repeats_removed():
    assert ids(dedupe_hits(HITS)) == [1, 3, 4]


def test_max_per_source():
    assert ids(dedupe_hits(HITS, max_per_source=1)) == [1]
    assert ids(dedupe_hits(HITS, max_per_source=2)) == [1, 3]


def test_dropped_repeat_does_not_count():
    hits = [
        {"id": 1, "text": "a", "source": "x"},
        {"id": 2, "text": "A", "source": "y"},
        {"id": 3, "text": "b", "source": "y"},
    ]
    assert ids(dedupe_hits(hits, max_per_source=1)) == [1, 3]


def test_missing_source():
    hits = [{"id": 1, "text": "a"}, {"id": 2, "text": "b"}]
    assert ids(dedupe_hits(hits, max_per_source=1)) == [1]


def test_empty():
    assert dedupe_hits([]) == []
