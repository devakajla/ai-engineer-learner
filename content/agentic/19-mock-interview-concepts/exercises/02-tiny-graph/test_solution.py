import pytest

from solution import next_node, run_graph


def test_next_node_plain_and_conditional_and_missing():
    edges = {"a": "b", "b": lambda s: "c" if s["ok"] else "a"}
    assert next_node(edges, "a", {}) == "b"
    assert next_node(edges, "b", {"ok": True}) == "c"
    assert next_node(edges, "b", {"ok": False}) == "a"
    assert next_node(edges, "c", {}) == "END", "a node with no edge ends the run"


def test_linear_graph():
    nodes = {"a": lambda s: {"x": s["x"] + 1}, "b": lambda s: {"x": s["x"] * 10}}
    out = run_graph(nodes, {"a": "b"}, "a", {"x": 1})
    assert out == {"state": {"x": 20}, "path": ["a", "b"]}


def test_loop_with_a_conditional_edge():
    nodes = {"work": lambda s: {"n": s["n"] + 1}}
    edges = {"work": lambda s: "work" if s["n"] < 3 else "END"}
    out = run_graph(nodes, edges, "work", {"n": 0})
    assert out["state"] == {"n": 3}
    assert out["path"] == ["work", "work", "work"]


def test_infinite_loop_is_stopped():
    nodes = {"spin": lambda s: {}}
    with pytest.raises(RuntimeError, match="recursion limit reached"):
        run_graph(nodes, {"spin": "spin"}, "spin", {}, max_steps=5)


def test_exactly_max_steps_is_allowed():
    nodes = {"spin": lambda s: {"n": s.get("n", 0) + 1}}
    edges = {"spin": lambda s: "spin" if s["n"] < 5 else "END"}
    assert run_graph(nodes, edges, "spin", {}, max_steps=5)["state"] == {"n": 5}


def test_a_node_can_set_the_next_choice_through_state():
    nodes = {"decide": lambda s: {"route": "left" if s["q"] < 0 else "right"},
             "left": lambda s: {"out": "L"}, "right": lambda s: {"out": "R"}}
    edges = {"decide": lambda s: s["route"]}
    assert run_graph(nodes, edges, "decide", {"q": -1})["state"]["out"] == "L"
    assert run_graph(nodes, edges, "decide", {"q": 4})["path"] == ["decide", "right"]
