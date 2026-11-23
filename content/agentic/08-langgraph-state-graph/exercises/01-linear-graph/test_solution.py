from solution import build_linear_graph, clean, shout


def test_nodes_return_only_the_changes():
    assert clean({"text": "  hi ", "steps": []}) == {"text": "hi", "steps": ["clean"]}
    assert shout({"text": "hi", "steps": []}) == {"text": "HI!", "steps": ["shout"]}


def test_graph_runs_the_nodes_in_order():
    app = build_linear_graph()
    out = app.invoke({"text": "  hello ", "steps": []})
    assert out == {"text": "HELLO!", "steps": ["clean", "shout"]}


def test_graph_can_run_many_times():
    app = build_linear_graph()
    assert app.invoke({"text": " a ", "steps": []})["text"] == "A!"
    assert app.invoke({"text": " b ", "steps": []})["steps"] == ["clean", "shout"], "each run starts fresh"


def test_stream_shows_one_update_per_node():
    app = build_linear_graph()
    updates = list(app.stream({"text": " x ", "steps": []}, stream_mode="updates"))
    assert [list(u)[0] for u in updates] == ["clean", "shout"]
