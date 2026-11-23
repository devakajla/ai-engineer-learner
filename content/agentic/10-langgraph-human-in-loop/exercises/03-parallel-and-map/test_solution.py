from solution import build_map_graph, build_parallel_graph


def test_parallel_branches_both_run_and_join():
    app = build_parallel_graph()
    out = app.invoke({"text": "hello big world", "words": 0, "chars": 0, "report": ""})
    assert out["words"] == 3 and out["chars"] == 15
    assert out["report"] == "3 words, 15 chars", "report must run once, after BOTH branches finished"


def test_report_runs_only_once():
    app = build_parallel_graph()
    updates = list(app.stream({"text": "a b", "words": 0, "chars": 0, "report": ""}, stream_mode="updates"))
    names = [list(u)[0] for u in updates]
    assert names.count("report") == 1
    assert names[-1] == "report"


def test_map_runs_the_worker_once_per_item():
    app = build_map_graph(lambda x: x * x)
    out = app.invoke({"items": [1, 2, 3, 4], "results": [], "total": 0})
    assert sorted(out["results"]) == [1, 4, 9, 16]
    assert out["total"] == 30


def test_map_with_one_item_and_with_many_items():
    app = build_map_graph(lambda x: x + 1)
    assert app.invoke({"items": [5], "results": [], "total": 0})["total"] == 6
    assert app.invoke({"items": list(range(20)), "results": [], "total": 0})["total"] == sum(range(1, 21))


def test_worker_function_is_used():
    seen = []

    def work(x):
        seen.append(x)
        return 0

    build_map_graph(work).invoke({"items": ["a", "b"], "results": [], "total": 0})
    assert sorted(seen) == ["a", "b"]
