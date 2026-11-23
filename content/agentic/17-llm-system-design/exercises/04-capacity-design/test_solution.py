from solution import design_components, required_replicas


def test_replicas_round_up_with_headroom():
    assert required_replicas(10, 500, 2000) == 4          # 2.5 * 1.3 = 3.25
    assert required_replicas(2, 1000, 1000) == 3          # 2.0 * 1.3 = 2.6
    assert required_replicas(10, 500, 2000, headroom=0.0) == 3
    assert required_replicas(10, 500, 2000, headroom=1.0) == 5


def test_always_at_least_one_replica():
    assert required_replicas(0, 500, 2000) == 1
    assert required_replicas(0.001, 10, 5000) == 1


def test_basic_design_has_the_always_parts_in_order():
    assert design_components({}) == [
        "api gateway with auth and rate limits",
        "llm client with timeouts and retries",
        "tracing and eval gate",
    ]


def test_each_requirement_adds_its_component():
    parts = design_components({"multi_tenant": True})
    assert "tenant isolation (per-tenant index or filters)" in parts
    assert "response cache" not in parts
    assert "access-controlled retrieval" in design_components({"private_docs": True})
    assert "incremental re-indexing" in design_components({"needs_freshness": True})
    assert "SSE streaming" in design_components({"needs_streaming": True})
    assert "human approval and audit log" in design_components({"high_risk_actions": True})


def test_high_traffic_adds_queue_and_cache():
    parts = design_components({"high_traffic": True})
    assert parts[-3:] == ["queue and autoscaled workers", "response cache", "tracing and eval gate"]


def test_full_requirements_in_a_fixed_order():
    everything = {k: True for k in ["multi_tenant", "private_docs", "needs_freshness", "high_traffic",
                                    "needs_streaming", "high_risk_actions"]}
    assert design_components(everything) == [
        "api gateway with auth and rate limits",
        "llm client with timeouts and retries",
        "tenant isolation (per-tenant index or filters)",
        "access-controlled retrieval",
        "incremental re-indexing",
        "queue and autoscaled workers",
        "response cache",
        "SSE streaming",
        "human approval and audit log",
        "tracing and eval gate",
    ]
