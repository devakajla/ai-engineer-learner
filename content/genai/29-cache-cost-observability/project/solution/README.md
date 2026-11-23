# DevDocs Copilot

Answers questions about API documentation, and shows where each answer came from.

## Setup

    uv sync
    export GROQ_API_KEY="your key from console.groq.com"

## Chat in the terminal

    uv run python -m copilot.cli

## Search (no model call needed for the vectors)

    uv run python -m copilot.search_cli "how do I delete a task"

## Look at your chunks

    uv run python -m copilot.ingest_cli docs

## Index and search your docs

    uv run python -m copilot.docs_cli index docs
    uv run python -m copilot.docs_cli search "how do I delete a task"

Compare the three ways: `search` (hybrid), `vector` and `keyword`.

## Ask your docs (RAG)

    uv run python -m copilot.rag_cli "how do I delete a task"

## Keep the index in sync

    uv run python -m copilot.docs_cli sync docs

## Ask as a user (copy access.example.json to access.json first)

    uv run python -m copilot.access_cli acme eng "how do I create a task"

## Score the search on your golden questions

    uv run python -m copilot.eval_cli evals/golden.json

## Full check with an LLM judge (uses tokens)

    uv run python -m copilot.eval_cli evals/golden.json answers

## Ask the agent about an OpenAPI spec

    uv run python -m copilot.agent_cli openapi.json "which endpoints change a task?"

## Agentic RAG (grade, rewrite, give up)

    uv run python -m copilot.agentic_cli "how do I remove a task"

## Guarded answers (input checks, PII hidden, tool allow-list)

    uv run python -m copilot.guard_cli "how do I delete a task? my email is sam@example.com"

## Trace a question and run the agent eval

    uv run python -m copilot.trace_cli ask "how do I delete a task"
    uv run python -m copilot.trace_cli eval evals/agent_cases.json baseline.json

## Serve Copilot over HTTP (JSON and streaming)

    uv run uvicorn copilot.server:build_default_app --factory --port 8100
    curl -N "http://localhost:8100/stream?question=how%20do%20I%20delete%20a%20task"

## Cache, rate limit and cost

The server now caches answers, limits each client (429 with Retry-After), and shows call counts and cost:

    curl "http://localhost:8100/stats"
