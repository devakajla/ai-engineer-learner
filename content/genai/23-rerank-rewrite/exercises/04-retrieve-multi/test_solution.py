from solution import retrieve_multi

DB = {
    "q1": [{"id": "a", "text": "A"}, {"id": "b", "text": "B"}],
    "q2": [{"id": "b", "text": "B2"}, {"id": "c", "text": "C"}],
    "q3": [],
}


def retrieve(query, k):
    return DB[query][:k]


def test_fusion():
    out = retrieve_multi(retrieve, ["q1", "q2"], k=3)
    assert [h["id"] for h in out] == ["b", "a", "c"]
    assert out[0]["text"] == "B", "keep the hit seen first"


def test_k_limit():
    out = retrieve_multi(retrieve, ["q1", "q2"], k=2)
    assert [h["id"] for h in out] == ["b", "a"]
    assert len(out) == 2


def test_empty_results():
    assert retrieve_multi(retrieve, ["q3"], k=3) == []
    assert retrieve_multi(retrieve, [], k=3) == []


def test_single_query_keeps_order():
    out = retrieve_multi(retrieve, ["q1"], k=2)
    assert [h["id"] for h in out] == ["a", "b"]
