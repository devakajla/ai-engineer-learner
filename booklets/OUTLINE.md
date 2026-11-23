# Booklets: outline

Seven PDF booklets for Dev's daily reading. They are not linked from the website. Goal: job-ready AI Engineer.

## Rules for every booklet
- English in simple words. Short sentences. Explain a jargon word the first time it appears.
- **Understanding first (revised 2026-11-22): about 50% explanation and 50% code.** Code alone is not enough. Every concept follows this order: plain everyday meaning, why it exists, a picture or mental model, a SMALL example (3-8 lines) with output as `# ->`, then a line-by-line 'what just happened' in words, then the trap. Few big code dumps. Long code only for guided builds, and each block must be explained right after it. Applies to ALL booklets (FastAPI needs a revision pass for this).
- Many visuals: inline SVG diagrams (flows, boxes and arrows, tables). One diagram per big idea.
- Page 1 after the title is a **Quick Reference**: the most used methods, commands or snippets, so Dev can revise any time.
- Every chapter has: why it matters, concepts with examples, "Common mistakes", "Interview corner" (from the Backend booklet on), and chapter-end **exercises** (with answers at the end of the booklet).
- No length limit. No topic is shortened.
- The last chapter of GenAI, Agentic AI, Backend, DevOps and System Design is an interview question bank.

---

## 1. Backend (first)
Quick reference: HTTP methods and status codes, SQL cheat sheet, Redis commands, cache and queue patterns.
Each chapter ends with a "How FastAPI does this" box.
1. How a backend works: client, server, database
2. HTTP and REST: methods, status codes, idempotency, pagination, versioning
3. SQL and Postgres: joins, GROUP BY, HAVING, subqueries, CTEs, window functions
4. Schema design and normalization; indexes (B-tree, composite, covering); `EXPLAIN ANALYZE`; the N+1 problem
5. Transactions, ACID, isolation levels, locking
6. SQL vs NoSQL; JSONB
7. Auth: password hashing, sessions vs JWT, OAuth2, API keys, authn vs authz
8. Caching and Redis: data types, expiry, cache-aside, invalidation, stampede
9. Queues and workers: Celery/ARQ, retries, dead-letter queues, brokers (RabbitMQ, Kafka basics)
10. Rate limiting: token bucket, sliding window
11. Concurrency, connection pooling, backpressure
12. Logging, metrics, tracing (OpenTelemetry basics); API security (OWASP top 10, secrets)
13. Clean layers: routes, services, repositories; patterns that come up (strategy, factory, adapter, observer, repository)
14. Interview question bank

## 2. Python
Quick reference: string, list, dict, set, tuple methods; built-ins; `itertools`, `collections`, `pathlib`, `json`, `datetime`, `re`.
1. Setup, first program, how Python runs
2. Variables, numbers, strings
3. Conditions and loops
4. Lists, tuples, sets, dicts
5. Functions
6. Files, modules, errors and custom exceptions
7. Comprehensions and sorting
8. Data model: mutability, references, shallow vs deep copy, dunder methods
9. OOP: classes, dataclasses, ABCs, composition vs inheritance, SOLID basics
10. Iterators, generators, `yield`, generator pipelines
11. Closures, decorators (with arguments), `functools`
12. Context managers, `contextlib`
13. Type hints, `typing`, Pydantic
14. Concurrency: GIL, threading vs multiprocessing vs asyncio
15. asyncio in depth: event loop, `gather`, tasks, semaphores, timeouts, cancellation
16. Testing with pytest (fixtures, mocking, async tests); packaging with `uv`, `pyproject.toml`
17. Profiling and performance (`cProfile`, avoiding N+1 calls)
18. Interview question bank

## 3. FastAPI
Quick reference: route decorators, parameter types, `Depends`, status codes, response classes, `TestClient`, common settings.
1. HTTP and REST recap
2. First app
3. Path and query parameters
4. Request bodies and Pydantic (validators, unions)
5. Responses, status codes, errors
6. Project structure and `pydantic-settings`
7. Dependency injection (DB sessions, auth, settings)
8. SQLAlchemy 2.0 async and Alembic
9. Async endpoints and the event loop (never block it)
10. Middleware, CORS, exception handlers, logging, lifespan
11. Auth: JWT, OAuth2 password flow, API keys, scopes
12. Background tasks vs a real queue
13. Streaming: SSE and WebSockets
14. Forms, files, cookies
15. Testing
16. Docker and deployment
17. LLM backend patterns (timeouts, streaming tokens, cost limits)
18. A full mini-project
19. Interview question bank

## 4. GenAI
Quick reference: SDK calls and parameters, token math, numpy cosine, Chroma and pgvector calls, retrieval metrics.
1. AI, ML, GenAI, LLMs; how LLMs work (transformers, attention, next-token prediction)
2. Tokens, tokenization (BPE), context windows, cost math
3. Your first API call, messages and roles
4. Sampling: temperature, top-p, max tokens, stop sequences
5. Streaming, errors, rate limits, retries with backoff, provider fallbacks
6. Prompt engineering: system prompts, few-shot, chain of thought, templates, prompt caching
7. Structured output: JSON mode, schema-constrained output, Pydantic parsing and retry
8. Tool and function calling across providers (OpenAI, Anthropic, Gemini, Groq)
9. Chat memory and conversation summaries
10. Embeddings: what they are, models, dimensions, cosine vs dot vs L2
11. Document parsing (PDF, tables, HTML) and chunking (fixed, recursive, semantic; size and overlap)
12. Vector DBs: Chroma, pgvector, Qdrant; ANN indexes (HNSW, IVF), recall vs latency; metadata filters; index updates and re-embedding
13. Keyword search (BM25), hybrid search, reciprocal rank fusion, cross-encoder reranking
14. The RAG pipeline end to end; grounded answers and citations
15. Advanced retrieval: query rewriting, multi-query, HyDE, parent-child, contextual retrieval, GraphRAG idea, text-to-SQL
16. Evals: retrieval metrics (recall@k, precision@k, MRR), generation metrics (faithfulness, relevance), golden dataset, LLM-as-judge and its biases, RAGAS/DeepEval, regression evals in CI
17. Failure modes: hallucination, prompt injection, context overflow, PII; guardrails
18. Prompting vs RAG vs fine-tuning; long context vs RAG; open-source models (Hugging Face, Ollama, vLLM, quantization); fine-tuning basics (LoRA, PEFT, instruction tuning, RLHF idea)
19. Multimodal basics (vision, audio) and embeddings for images
20. Cost, latency and scale: semantic caching, batching, model routing, concurrency limits for LLM calls, multi-tenant vector isolation
21. Observability: tracing every LLM call, dashboards, feedback loops
22. Interview question bank

## 5. Agentic AI
Quick reference: LangChain and LangGraph building blocks (model, prompt, parser, tool, retriever, state graph).
1. What an agent is; workflow vs agent
2. The agent loop from scratch (LLM + tools + loop + stop condition), no framework
3. Tool design: clear schemas, idempotent tools, error messages the model can act on
4. Workflow patterns: prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer
5. Agent patterns: ReAct, plan-and-execute, router, reflection
6. LangChain basics: chat models, prompts, output parsers, LCEL chains, tools, retrievers
7. LangGraph: state, nodes, edges, conditional routing, checkpoints and persistence, streaming
8. Memory: short-term vs long-term; context engineering (what goes in the window)
9. Agentic RAG
10. Human-in-the-loop approval and interrupts
11. Multi-agent systems and when not to use them
12. MCP: what it is, writing a simple server and client
13. Guardrails: max steps, timeouts, cost caps, input and output validation, prompt injection through tools
14. Evaluating and tracing agents: task success rate, step count, tool-call accuracy; Langfuse/LangSmith
15. Deploying an agent behind FastAPI
16. Capstone: an agent with 3-5 real tools
17. Interview question bank

## 6. DevOps
Quick reference: git, Linux/shell, Docker and Compose commands, GitHub Actions snippet.
1. Git beyond basics: branching, rebase vs merge, PR workflow
2. Linux and shell: processes, ports, logs, ssh, permissions
3. Docker: Dockerfile, layers, multi-stage builds, slim images
4. Docker Compose: API + Postgres + Redis + worker
5. CI/CD with GitHub Actions: tests, lint, build, deploy
6. Serving: gunicorn/uvicorn workers, Nginx reverse proxy, health checks, graceful shutdown
7. Environment variables and secrets in production
8. AWS basics: EC2, S3, IAM, RDS, ECS or Lambda
9. Kubernetes concepts: pods, deployments, services
10. Logs, monitoring, alerts; cost awareness (GPU vs API)
11. Interview question bank

## 7. System Design
Quick reference: latency and size numbers every developer should know, estimation formulas, a design template.
1. How to approach a design question
2. Back-of-envelope estimation: QPS, storage, bandwidth
3. Scaling: vertical vs horizontal, load balancers, stateless services
4. Databases at scale: replication, sharding, read replicas
5. CAP theorem and consistency models
6. Caching layers, CDNs, queues, async processing
7. Classic designs: URL shortener, chat app, notification system, news feed
8. Low-level design: SOLID, clean architecture, patterns; practice: parking lot, rate limiter, LRU cache
9. LLM system design: RAG chatbot for 10k+ documents and 1k concurrent users
10. Document processing pipeline at scale (ingest, parse, embed, index)
11. LLM latency, cost, reliability, safety, observability, multi-tenant isolation
12. Interview question bank

## DSA
No booklet. Stays on the website, up to medium difficulty.
