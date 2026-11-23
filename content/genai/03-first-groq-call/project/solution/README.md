# DevDocs Copilot

Answers questions about API documentation, and shows where each answer came from.

## Setup

    uv sync
    export GROQ_API_KEY="your key from console.groq.com"

## Try it

    uv run python -c "from copilot.llm import get_client, ask; print(ask(get_client(), 'Say hello'))"
