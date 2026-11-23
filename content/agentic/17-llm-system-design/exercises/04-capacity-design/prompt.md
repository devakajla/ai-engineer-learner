# How many servers, and which parts?

Two more design skills.

**Capacity.** A model server can produce some number of **tokens per second** (for all its users together). Your traffic needs `requests per second x tokens per request` tokens per second. Divide, add **headroom** for spikes (30% is a common start), and round **up**: you cannot run 3.25 servers.

**Components.** A good design answer starts from the **requirements** and picks the parts that they need, no more.

Write (`import math` is in the starter):

1. `required_replicas(requests_per_second, tokens_per_request, tokens_per_second_per_replica, headroom=0.3)`: `needed = rps * tokens_per_request / tokens_per_second_per_replica`, then `ceil(needed * (1 + headroom))`. Never less than 1.
2. `design_components(requirements)`: `requirements` is a dict of booleans (keys may be missing). Return a list of strings **in this order**:
   - always first: `"api gateway with auth and rate limits"`, `"llm client with timeouts and retries"`
   - `multi_tenant`: `"tenant isolation (per-tenant index or filters)"`
   - `private_docs`: `"access-controlled retrieval"`
   - `needs_freshness`: `"incremental re-indexing"`
   - `high_traffic`: `"queue and autoscaled workers"`, then `"response cache"`
   - `needs_streaming`: `"SSE streaming"`
   - `high_risk_actions`: `"human approval and audit log"`
   - always last: `"tracing and eval gate"`

```python
required_replicas(10, 500, 2000)
# -> 4      (2.5 replicas of work, 3.25 with headroom, rounded up)
design_components({"high_traffic": True})[-3:]
# -> ['queue and autoscaled workers', 'response cache', 'tracing and eval gate']
```

**Think first:** why start a design from the requirements and not from your favourite tools?

**Hint:** `requirements.get("multi_tenant")` is `None` (false) when the key is missing.
