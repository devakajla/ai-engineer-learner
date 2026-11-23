from solution import apply_sync, content_hash


class Embedder:
    def __init__(self):
        self.calls = []

    def __call__(self, texts):
        self.calls.append(list(texts))
        return [[float(len(t))] for t in texts]


def test_first_run():
    index, embed = {}, Embedder()
    out = apply_sync(index, {"b": "yy", "a": "x"}, embed)
    assert out == {"added": 2, "updated": 0, "deleted": 0, "same": 0}
    assert embed.calls == [["x", "yy"]], "one call, sorted by id"
    assert index["a"] == {"hash": content_hash("x"), "vector": [1.0]}


def test_second_run_embeds_nothing():
    index, embed = {}, Embedder()
    apply_sync(index, {"a": "x"}, embed)
    embed.calls.clear()
    out = apply_sync(index, {"a": "x"}, embed)
    assert out["same"] == 1 and embed.calls == []


def test_update_and_delete():
    index, embed = {}, Embedder()
    apply_sync(index, {"a": "x", "b": "y", "c": "z"}, embed)
    embed.calls.clear()
    out = apply_sync(index, {"a": "x changed", "b": "y", "d": "new"}, embed)
    assert out == {"added": 1, "updated": 1, "deleted": 1, "same": 1}
    assert embed.calls == [["x changed", "new"]]
    assert set(index) == {"a", "b", "d"}
    assert index["a"]["vector"] == [9.0]


def test_empty_docs_clears_index():
    index, embed = {}, Embedder()
    apply_sync(index, {"a": "x"}, embed)
    apply_sync(index, {}, embed)
    assert index == {}
