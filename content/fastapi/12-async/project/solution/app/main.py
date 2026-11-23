from fastapi import FastAPI

from app.api.routes import health, tasks
from app.core.config import get_settings


def create_app() -> FastAPI:
    """Application factory: builds a fully wired app (handy for tests and workers).

    The database schema is managed by Alembic migrations: run `uv run alembic upgrade head`.
    """
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="A task-manager REST API",
        debug=settings.debug,
    )
    app.include_router(health.router)
    app.include_router(tasks.router, prefix=settings.api_prefix)
    return app


app = create_app()
