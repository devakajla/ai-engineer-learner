---
title: "LLM system design: cost, latency, scale and safety"
summary: Learn a simple method for system design questions, do the cost, latency and capacity maths, and walk through three typical designs (RAG at scale, multi-tenant assistant, support agent).
plan_ids: []
---

"Design a document assistant for 10,000 employees." Interviewers ask this for AI engineer jobs, and real projects start with the same questions. You have all the parts by now: models, RAG, agents, memory, safety, evals. System design is about **choosing and joining** them, with numbers.

There is no single right answer. Interviewers want to see that you ask good questions, do rough maths, name trade-offs and keep it simple.

## A five-step method

1. **Clarify the requirements.** Who are the users? How many? What is a good answer? What must never happen? What are the latency and cost limits? Is the data private, changing, multi-tenant?
2. **Estimate the numbers.** Requests per day, tokens per request, cost per month, requests per second at the peak, latency budget.
3. **Draw the simplest design** that meets the requirements. Name each box and what it does.
4. **Go deep on the hard parts.** Retrieval quality, safety, cost, failure handling.
5. **Say how you would measure and improve it.** Evals, tracing, a rollout plan.

> Start simple (lesson 1). Add a part only when a requirement needs it. Say which requirement.

## Step 2 in numbers

### Cost (exercise 1)

Prices are in dollars per **million** tokens, one for input and one for output.

```python
def request_cost(input_tokens, output_tokens, price_in, price_out):
    return (input_tokens * price_in + output_tokens * price_out) / 1_000_000

request_cost(1000, 500, 0.5, 1.5)
# -> 0.00125
# 1000 requests a day for a month, 2000 tokens in and 500 out:
# 1000 * 30 * 0.00175  ->  52.5 dollars
```

Look at what drives cost: **input tokens** (long prompts, retrieved chunks, chat history) are usually the biggest part. An agent sends its history again at every step, so a 6-step run costs much more than 6 times one call.

Ways to cut cost:

- a **smaller model** for easy steps, a big one only for hard steps (the router of GenAI lesson 33),
- **fewer and shorter chunks** in the prompt, and trimmed history (lesson 11),
- **caching** (below),
- **batching** work that is not urgent (many providers offer cheaper batch APIs; check yours),
- a **step cap** on agents (lessons 5 and 13).

### Caching (exercise 2)

Two kinds:

- **Response cache.** Same question (or the same meaning, checked with embeddings) gets a stored answer. No model call. A lookup is cheap but not free.
- **Prompt (prefix) cache.** The provider charges less for the start of the prompt if it saw it recently. Put the stable parts first (system prompt, tools, a long document) and the changing question last.

```python
cost_with_cache(1000, 0.3, 0.01, 0.0001)
# -> 7.1     (700 model calls and 1000 cheap lookups, instead of 10.0)
```

A cache is only safe for answers that do not depend on the user. **Never share a cached answer between users with different access rights** (lesson 15 and GenAI lesson 40). Put the user's permissions into the cache key, or do not cache.

### Latency (exercise 3)

Steps that depend on each other add up. Independent steps run in parallel, so only the slowest counts. The slowest chain is the **critical path**.

```
auth 20 -> [ vector 80 | keyword 50 | profile 30 ] -> rerank 120 -> llm 900
total = 20 + 80 + 120 + 900 = 1120 ms
```

To go faster, work on the critical path: stream the answer so the user sees the first words early (time to first token matters more than total time for chat), run independent searches in parallel, use a smaller or faster model, shorten the prompt, cache. Making `keyword_search` faster in the example changes nothing, because it is not on the critical path.

Report **p95** latency (the time that 95% of requests beat), not only the average. Users remember the slow ones.

### Capacity (exercise 4)

```python
needed = requests_per_second * tokens_per_request / tokens_per_second_per_replica
replicas = ceil(needed * 1.3)       # 30% headroom for spikes
```

With a hosted API your "capacity" is the **rate limit** (requests and tokens per minute). Plan for it: queue, retry with backoff (GenAI lesson 6), fall back to another model, and spread load.

## The parts of a typical design

```
user -> API gateway (auth, rate limit) -> app service
                                            |-- cache lookup
                                            |-- router / guard (input checks)
                                            |-- retrieval (search + filters by tenant and permission)
                                            |-- agent or chain (LLM client: timeout, retry, fallback)
                                            |-- output checks (citations, safety)
                                          -> stream answer back
side paths: ingestion pipeline (parse, chunk, embed, upsert), queue + workers,
            tracing + metrics, eval set + CI gate
```

`design_components` in exercise 4 picks parts from requirements, so you practise saying "this requirement needs this part".

## Three typical designs

### 1. RAG assistant at scale

**Requirements:** 10,000 users, company documents, answers with citations, under 3 seconds to first token.

- **Ingestion:** parse (PDF, HTML), clean, chunk, add metadata (source, date, owner, access list), embed, store in a vector database with a keyword index (hybrid search, GenAI lesson 18). Re-index **incrementally** by content hash (GenAI lesson 39).
- **Query path:** guard, rewrite the question if needed, hybrid search with **permission filters**, rerank the top 20 to 5, build the prompt with citations, stream the answer, check that every citation exists.
- **Scale:** the vector index is sharded or uses a managed service. The model call is the bottleneck: cache, rate-limit and queue.
- **Failures:** if search returns nothing useful, say so. If the model is down, fall back to another model or show the sources only.
- **Measure:** recall@k for retrieval, faithfulness and citation checks, thumbs up/down, p95 latency, cost per answer.

### 2. Multi-tenant assistant (a product for many companies)

The new problem is **isolation**: company A must never see company B's data.

- Every record and every chunk carries a `tenant_id`. **Every** query filters on it, enforced in one place in code, not left to each developer. Test it with an attack case.
- Options: one index per tenant (strong isolation, more cost), or one index with filters (cheaper, more risk). Large or regulated tenants get their own.
- Separate caches, memory and logs per tenant. Limit and meter cost **per tenant** (noisy neighbours).
- Keys and secrets per tenant for their own integrations.

### 3. Customer support agent with actions

**Requirements:** answer from help docs, and do small actions (look up an order, start a refund).

- A **workflow or a small agent** with a few tools. Read tools run freely. The refund tool is **medium risk**: limits on the amount, and a human approval above it (lesson 15).
- **Guardrails:** quarantine tool output, strict argument validation, a step cap, an audit log.
- **Handoff to a person** when the agent is unsure or the user is angry. Show the whole trace to the human.
- **Memory:** short-term in the thread, long-term facts per customer (lesson 11), with deletion on request.
- **Measure:** resolution rate, handoff rate, wrong-action rate (should be near zero), cost per ticket, trajectory evals (lesson 16).

## Reliability and safety checklist

- Timeouts and retries with backoff on every model and tool call.
- A **fallback** model and a graceful message when everything fails.
- Idempotent actions (a retry must not refund twice).
- Input and output guards, prompt-injection defences, least privilege (lesson 15).
- Privacy: redact personal data in logs, set retention, do not train on user data without consent, check where the provider stores data.
- Versioned prompts and models, a staged rollout (a small share of traffic first), and an easy rollback.
- Eval gate in CI (lesson 16) and online monitoring with alerts.

## Try it live

1. Pick one design above. Write the five steps on one page: requirements, numbers, boxes, hard parts, measures.
2. Use your `monthly_cost` with real prices for your model. Which part of the prompt is the biggest?
3. Add a response cache to your DevDocs assistant (a dict keyed by the question text). Measure the hit rate on 20 questions where 5 are repeated.
4. Time each stage of your pipeline with `traced_call` (lesson 16). Find the critical path. Do your searches run in parallel?
5. Say the whole design out loud in 5 minutes. Record it. Listen for missing numbers and missing trade-offs.

## A little deeper

- **Semantic cache risks.** "Cancel my order" and "Cancel my order 1234" are close in meaning but need different actions. Cache only questions whose answer is general.
- **Queues for long jobs.** Anything that takes more than a few seconds should be a background job with a status endpoint or a webhook (FastAPI lesson 19).
- **Multi-region and data residency.** Some data must stay in one country. Choose the region of the provider and of the vector store.
- **Build vs buy.** Managed vector databases and gateways save time. Self-hosting saves money at scale and gives control. Decide with numbers.
- **Model gateways.** A small service in front of all model calls gives you one place for keys, retries, fallbacks, caching, budgets and logs. Several products offer this (names change).
- **Degrade, do not die.** When the model is slow, switch to a smaller model, shorter context, or search results only.
- **Cost of quality.** A reranker, a judge or a second model call each add cost and latency. Keep them only if the eval shows a gain.

## Common mistakes

- Starting with tools ("we will use Kubernetes and three agents") before requirements.
- No numbers: no tokens, no cost, no requests per second.
- Forgetting that agents re-send history at every step.
- Caching answers across users with different permissions.
- Filtering by tenant in some code paths and forgetting it in others.
- One model for every task, when a small model would do for most.
- No fallback and no timeout on the model call.
- A design without a way to measure quality.

## Interview corner

**Walk me through designing a RAG assistant for a company.**
Clarify users, data and limits. Estimate traffic and cost. Ingestion (parse, chunk, metadata, embed, incremental re-index). Query path (guard, hybrid search with permission filters, rerank, prompt with citations, stream). Then scale, failures, safety and how I would measure it.

**How do you reduce the cost of an LLM application?**
Smaller models for easy steps, shorter prompts (fewer chunks, trimmed history), response and prompt caching, batching, step caps for agents, and routing. Measure each change with an eval.

**How do you keep latency low?**
Stream the answer, run independent steps in parallel, shorten the critical path, use faster models, cache, and track p95, not the average.

**How do you isolate tenants?**
A tenant id on every record, mandatory filters enforced in one place, separate caches and logs, per-tenant limits, and stronger isolation (own index) for large or regulated tenants. Test with attack cases.

**What if the LLM provider goes down or is rate limited?**
Timeouts, retries with backoff, a queue, a fallback model, and a graceful message. Keep idempotent actions so retries are safe.

**How do you roll out a change to a prompt or model?**
Run the eval gate offline, release to a small share of traffic, watch quality, cost and latency, and keep a rollback.

## Summary

- Method: **clarify, estimate, design simply, go deep, measure**.
- Cost = tokens x price. Input tokens and agent history dominate. Cut with small models, short prompts, caches and step caps.
- Response caches skip the model. Prompt caches make a stable prefix cheaper. Never share cached answers across permission boundaries.
- Latency: independent steps run in parallel, dependent steps add up. Work on the **critical path**. Stream. Watch p95.
- Capacity = rate x tokens / throughput, plus headroom, rounded up. For hosted APIs, plan for rate limits.
- Typical designs: RAG at scale (ingestion, hybrid search, permission filters, rerank, citations), multi-tenant (isolation everywhere), support agent (risk tiers, approvals, handoff).
- Always: timeouts, retries, fallbacks, idempotency, safety layers, privacy, versions, rollout, evals and monitoring.
- Reference: `reference/agentic-langchain-langgraph.md`.
