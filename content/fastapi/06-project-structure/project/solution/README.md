# TaskFlow

A task-manager REST API built with FastAPI.

## Run locally

    cp .env.example .env
    uv run fastapi dev app/main.py

## Configuration

Settings are read from environment variables (or `.env`); see `.env.example`.

## Endpoints

- GET /health
- GET /api/v1/tasks, POST /api/v1/tasks
- GET /api/v1/tasks/{id}, PATCH /api/v1/tasks/{id}, DELETE /api/v1/tasks/{id}
