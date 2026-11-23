from solution import drop_stale

HITS = [
    {"id": "a", "updated": "2026-11-01"},
    {"id": "b", "updated": "2025-01-01"},
    {"id": "c"},
    {"id": "d", "updated": "2026-12-25"},
]


def test_drop_old():
    out = drop_stale(HITS, "2026-11-23", 365)
    assert [h["id"] for h in out] == ["a", "c", "d"]


def test_exact_boundary_kept():
    out = drop_stale([{"id": "x", "updated": "2026-11-13"}], "2026-11-23", 10)
    assert len(out) == 1


def test_one_day_over_dropped():
    out = drop_stale([{"id": "x", "updated": "2026-11-12"}], "2026-11-23", 10)
    assert out == []


def test_empty():
    assert drop_stale([], "2026-11-23", 10) == []
