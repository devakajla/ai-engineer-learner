from solution import expand_to_parents

PARENTS = {"p1": "section one", "p2": "section two"}
PARENT_OF = {"c1": "p1", "c2": "p1", "c3": "p2"}


def test_merge_same_parent():
    hits = [{"id": "c1", "text": "t1", "score": 0.5}, {"id": "c2", "text": "t2", "score": 0.9}]
    assert expand_to_parents(hits, PARENT_OF, PARENTS) == [{"id": "p1", "text": "section one", "score": 0.9}]


def test_order_by_first_hit():
    hits = [
        {"id": "c3", "text": "t3", "score": 0.8},
        {"id": "c1", "text": "t1", "score": 0.7},
        {"id": "c2", "text": "t2", "score": 0.6},
    ]
    out = expand_to_parents(hits, PARENT_OF, PARENTS)
    assert [h["id"] for h in out] == ["p2", "p1"]
    assert out[1]["score"] == 0.7


def test_no_parent_stays():
    hits = [{"id": "x", "text": "own", "score": 0.4}, {"id": "c3", "text": "t3", "score": 0.3}]
    out = expand_to_parents(hits, PARENT_OF, PARENTS)
    assert out == [{"id": "x", "text": "own", "score": 0.4}, {"id": "p2", "text": "section two", "score": 0.3}]


def test_empty_and_input_unchanged():
    assert expand_to_parents([], PARENT_OF, PARENTS) == []
    hits = [{"id": "c1", "text": "t1", "score": 0.5}]
    expand_to_parents(hits, PARENT_OF, PARENTS)
    assert hits == [{"id": "c1", "text": "t1", "score": 0.5}]
