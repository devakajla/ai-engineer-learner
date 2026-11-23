from solution import make_hits

CHUNKS = [
    {"id": "a", "text": "x", "source": "s", "heading": ""},
    {"id": "b", "text": "y", "source": "s", "heading": "H"},
    {"id": "c", "text": "z", "source": "s", "heading": ""},
]


def test_best_first_and_k():
    out = make_hits(CHUNKS, [0.2, 0.9, 0.5], k=2)
    assert [h["id"] for h in out] == ["b", "c"]
    assert out[0]["score"] == 0.9 and out[0]["heading"] == "H"


def test_min_score():
    out = make_hits(CHUNKS, [0.2, 0.9, 0.5], k=3, min_score=0.5)
    assert [h["id"] for h in out] == ["b", "c"]


def test_ties_keep_order():
    out = make_hits(CHUNKS, [0.5, 0.5, 0.5], k=3)
    assert [h["id"] for h in out] == ["a", "b", "c"]


def test_k_zero_and_empty():
    assert make_hits(CHUNKS, [1, 1, 1], k=0) == []
    assert make_hits([], [], k=3) == []


def test_originals_not_changed():
    make_hits(CHUNKS, [0.2, 0.9, 0.5], k=3)
    assert "score" not in CHUNKS[0]
