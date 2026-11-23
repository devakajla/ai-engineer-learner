import math


def required_replicas(requests_per_second, tokens_per_request, tokens_per_second_per_replica, headroom=0.3):
    needed = requests_per_second * tokens_per_request / tokens_per_second_per_replica
    return max(1, math.ceil(needed * (1 + headroom)))


def design_components(requirements):
    parts = ["api gateway with auth and rate limits", "llm client with timeouts and retries"]
    if requirements.get("multi_tenant"):
        parts.append("tenant isolation (per-tenant index or filters)")
    if requirements.get("private_docs"):
        parts.append("access-controlled retrieval")
    if requirements.get("needs_freshness"):
        parts.append("incremental re-indexing")
    if requirements.get("high_traffic"):
        parts.append("queue and autoscaled workers")
        parts.append("response cache")
    if requirements.get("needs_streaming"):
        parts.append("SSE streaming")
    if requirements.get("high_risk_actions"):
        parts.append("human approval and audit log")
    parts.append("tracing and eval gate")
    return parts
