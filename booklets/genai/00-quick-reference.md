# Quick Reference

Keep this page open while you read and while you build. It holds the calls, numbers and patterns you use most. Everything here is explained in the chapters.

## What is in this booklet

| Part | Chapters | You learn |
| --- | --- | --- |
| Foundations | 1 to 2 | how an LLM works, tokens, context, cost |
| Using the API | 3 to 5 | messages, sampling settings, streaming, errors, retries |
| Prompts and tools | 6 to 9 | prompt patterns, JSON output, tool calling, chat memory |
| Retrieval | 10 to 13 | embeddings, chunking, vector databases, hybrid search, reranking |
| RAG | 14 to 15 | the full pipeline, citations, advanced retrieval |
| Quality and safety | 16 to 17 | evals, failure modes, guardrails |
| Choosing and running | 18 to 21 | RAG vs fine-tuning, open models, multimodal, cost and scale, observability |
| Practice | 22 | 80 interview questions, drills, then answers to all exercises |

**Suggested daily rhythm (about 2 hours):** 40 minutes reading one chapter, 40 minutes typing and running its examples, 20 minutes on the exercises, 20 minutes saying the interview corner aloud. Do chapters 1 to 9 first, then 10 to 17 as one block (you build a small RAG), then 18 to 22.

> **Honesty note.** Offline pieces (tokens, cosine, chunking, BM25, RRF, metrics, Chroma with a toy embedder, retries and tool loops with fake clients) were run. Real calls to Groq, real embedding models, pgvector, Qdrant, Hugging Face, Ollama and vLLM were **not** run. Model names change often: check `console.groq.com/docs/models`.

## The API call (Groq)

```python
from groq import Groq
client = Groq()    # reads GROQ_API_KEY
r = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "system", "content": "..."},
              {"role": "user", "content": "..."}],
    temperature=0.2, max_completion_tokens=300,
)
r.choices[0].message.content      # the answer
r.choices[0].finish_reason        # "stop" or "length"
r.usage.prompt_tokens, r.usage.completion_tokens, r.usage.total_tokens
```

| Parameter | Meaning |
| --- | --- |
| `messages` | roles: system, user, assistant, tool |
| `temperature` | 0 steady, 1 varied |
| `top_p` | keep tokens that add up to p |
| `max_completion_tokens` | output cap |
| `stop` | strings that end the answer |
| `seed` | repeatable sampling, if supported |
| `stream=True` | pieces arrive as `chunk.choices[0].delta.content` |
| `response_format={"type": "json_object"}` | valid JSON syntax |
| `tools`, `tool_choice` | tool calling |
| `timeout` | seconds, also on `Groq(timeout=..., max_retries=...)` |

## Errors

| Error | HTTP | Retry? |
| --- | --- | --- |
| `BadRequestError` | 400 | no |
| `AuthenticationError` | 401 | no |
| `PermissionDeniedError` | 403 | no |
| `NotFoundError` | 404 | no |
| `RateLimitError` | 429 | yes, with backoff |
| `InternalServerError` | 5xx | yes |
| `APITimeoutError`, `APIConnectionError` | none | yes |

Backoff: `wait = base * 2 ** (attempt - 1) + random.random() * 0.1`.

## Token and cost math

```python
import tiktoken
enc = tiktoken.get_encoding("cl100k_base")
len(enc.encode("Hello, world!"))                 # an estimate; models differ
cost = in_tokens / 1e6 * in_price + out_tokens / 1e6 * out_price
```

Rough rule: 1 token is about 4 English letters, or three quarters of a word. 1,200 input and 300 output tokens at 0.05 and 0.08 dollars per million cost 0.000084 dollars.

## Similarity with numpy

```python
import numpy as np
cos = x @ y / (np.linalg.norm(x) * np.linalg.norm(y))      # cosine
M = M / np.linalg.norm(M, axis=1, keepdims=True)            # normalise rows
scores = M @ (q / np.linalg.norm(q))                        # all scores at once
top = np.argsort(-scores)[:k]                               # best k indexes
```

## Chroma

```python
import chromadb
db = chromadb.PersistentClient(path="./chroma")             # or EphemeralClient()
col = db.get_or_create_collection("docs", embedding_function=None,
                                  metadata={"hnsw:space": "cosine"})
col.add(ids=[...], embeddings=[...], documents=[...], metadatas=[...])
col.query(query_embeddings=[q], n_results=5, where={"tenant": "a"})
col.upsert(...)   col.delete(ids=[...])   col.get(ids=[...])   col.count()
```

Result `distances`: smaller is better (cosine distance is 1 minus similarity).

## pgvector

```sql
CREATE EXTENSION vector;
CREATE TABLE chunks (id serial PRIMARY KEY, body text, embedding vector(384), tenant_id int);
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops);
SELECT id, body FROM chunks WHERE tenant_id = 7
ORDER BY embedding <=> '[...]' LIMIT 5;       -- <=> cosine distance
```

## Retrieval patterns

| Pattern | One line |
| --- | --- |
| chunking | 200 to 500 tokens, 10 to 20 percent overlap, split on structure |
| hybrid | BM25 plus vectors, merged with RRF |
| RRF | score = sum of `1 / (60 + rank)` over the lists |
| rerank | retrieve 20 to 50, cross-encoder keeps 3 to 8 |
| no answer | score below threshold gives "I do not know", no model call |

## Metrics

| Metric | Meaning |
| --- | --- |
| precision@k | relevant share of the top k |
| recall@k | share of all relevant items found in the top k |
| MRR | average of 1 / rank of the first relevant result |
| faithfulness | every claim supported by the context |

## Settings by task

| Task | Temperature |
| --- | --- |
| classify, extract, JSON, RAG answer | 0 to 0.2 |
| chat | 0.5 to 0.7 |
| brainstorm | 0.9 to 1.2 |

## Patterns to remember

- Fake client for tests: a `SimpleNamespace` with `chat.completions.create` that records kwargs.
- Repair loop: ask, validate with Pydantic, send the error back, limit tries, then raise.
- Tool loop: call, run tools, append `assistant` and `tool` messages, stop on no tool calls or `max_steps`.
- Cache: exact first, semantic with a strict threshold.
- Isolation: tenant filter in the database query, never in the prompt.
