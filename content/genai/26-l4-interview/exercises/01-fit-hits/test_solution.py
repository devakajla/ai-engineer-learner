from solution import fit_hits

HITS = [{"text": "a b c"}, {"text": "d e"}, {"text": "f"}]


def test_fits():
    assert fit_hits(HITS, 5) == HITS[:2]
    assert fit_hits(HITS, 6) == HITS


def test_stops_at_first_miss():
    assert fit_hits(HITS, 4) == HITS[:1]
    hits = [{"text": "a b c d"}, {"text": "x"}]
    assert fit_hits(hits, 3) == [], "must not skip to a later, smaller hit"


def test_zero_and_empty():
    assert fit_hits(HITS, 0) == []
    assert fit_hits([], 10) == []
    assert fit_hits(HITS, -3) == []


def test_extra_spaces_do_not_count():
    assert fit_hits([{"text": "  a   b  "}], 2) == [{"text": "  a   b  "}]


def test_input_unchanged():
    before = list(HITS)
    fit_hits(HITS, 5)
    assert HITS == before
