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
