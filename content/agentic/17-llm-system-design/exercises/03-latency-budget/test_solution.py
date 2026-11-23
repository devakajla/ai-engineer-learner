from solution import critical_path, latency_report, total_latency

# Groups run one after another. Items inside a group run at the same time.
STAGES = [
    [("auth", 20)],
    [("vector_search", 80), ("keyword_search", 50), ("load_profile", 30)],
    [("rerank", 120)],
    [("llm", 900)],
]


def test_total_adds_groups_and_takes_the_slowest_inside_a_group():
    assert total_latency(STAGES) == 20 + 80 + 120 + 900
    assert total_latency([]) == 0
    assert total_latency([[]]) == 0


def test_critical_path_is_the_slowest_item_of_each_group():
    assert critical_path(STAGES) == [("auth", 20), ("vector_search", 80), ("rerank", 120), ("llm", 900)]
    assert critical_path([[], [("a", 1), ("b", 1)]]) == [("a", 1)], "empty groups are skipped, ties keep the first"


def test_report_within_budget():
    assert latency_report(STAGES, 1500) == {"total_ms": 1120, "ok": True, "over_by": 0, "biggest": "llm"}


def test_report_over_budget_names_the_biggest_stage():
    assert latency_report(STAGES, 1000) == {"total_ms": 1120, "ok": False, "over_by": 120, "biggest": "llm"}


def test_exactly_on_budget_is_ok():
    assert latency_report(STAGES, 1120)["ok"] is True


def test_empty_pipeline():
    assert latency_report([], 100) == {"total_ms": 0, "ok": True, "over_by": 0, "biggest": None}


def test_running_the_searches_in_parallel_saves_time():
    sequential = [[("auth", 20)], [("vector_search", 80)], [("keyword_search", 50)], [("load_profile", 30)]]
    parallel = [[("auth", 20)], [("vector_search", 80), ("keyword_search", 50), ("load_profile", 30)]]
    assert total_latency(sequential) - total_latency(parallel) == 80
