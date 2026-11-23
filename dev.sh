#!/usr/bin/env bash
# Starts the API (:8000) and the Next.js UI (:3000). Ctrl+C stops both.
set -e
cd "$(dirname "$0")"
trap 'kill 0' EXIT
uv run uvicorn app.main:app --reload --port 8000 &
(cd frontend && npm run dev) &
wait
