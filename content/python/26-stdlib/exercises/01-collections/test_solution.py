from collections import defaultdict

from solution import RecentEvents, group_by_domain, top_words


def test_top_words():
    assert top_words("the cat and THE hat the end", 2) == [("the", 3), ("cat", 1)]
    assert top_words("", 3) == []


def test_group_by_domain():
    result = group_by_domain(["a@x.io", "b@y.io", "c@x.io"])
    assert result == {"x.io": ["a@x.io", "c@x.io"], "y.io": ["b@y.io"]}
    assert type(result) is dict, "return a plain dict, not the defaultdict"


def test_recent_events():
    r = RecentEvents(2)
    for e in (1, 2, 3):
        r.add(e)
    assert r.items() == [2, 3]
    assert RecentEvents(5).items() == []
