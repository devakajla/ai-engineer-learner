# DevDocs Copilot

Answers questions about API documentation, and shows where each answer came from.

## Setup

    uv sync
    export GROQ_API_KEY="your key from console.groq.com"

## Chat in the terminal

    uv run python -m copilot.cli

## Search (no model call needed for the vectors)

    uv run python -m copilot.search_cli "how do I delete a task"
