from solution import build_clean_subgraph, build_pipeline


def test_subgraph_works_alone():
    out = build_clean_subgraph().invoke({"text": "  HeLLo  ", "log": []})
    assert out["text"] == "hello"


def test_pipeline_uses_the_subgraph_as_a_node():
    out = build_pipeline().invoke({"text": "  HeLLo  ", "log": []})
    assert out == {"text": "hello!", "log": ["cleaned", "finished"]}


def test_pipeline_shows_clean_as_one_step():
    updates = list(build_pipeline().stream({"text": " A ", "log": []}, stream_mode="updates"))
    assert [list(u)[0] for u in updates] == ["clean", "tag", "finish"], "the subgraph is one node from the parent's view"


def test_pipeline_is_reusable():
    app = build_pipeline()
    assert app.invoke({"text": " A ", "log": []})["text"] == "a!"
    assert app.invoke({"text": " B ", "log": []})["text"] == "b!"
