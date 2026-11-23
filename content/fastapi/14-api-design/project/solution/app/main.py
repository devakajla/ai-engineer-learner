from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.errors import register_exception_handlers
from app.api.middleware import register_middleware
from app.api.routes import health, tasks
from app.core.config import get_settings
from app.core.logging import setup_logging


def create_app() -> FastAPI:
    """Application factory: builds a fully wired app (handy for tests and workers).

    The database schema is managed by Alembic migrations: run `uv run alembic upgrade head`.
    """
    settings = get_settings()
    setup_logging(settings.log_level)
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="A task-manager REST API",
        debug=settings.debug,
    )
    register_middleware(app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)
    app.include_router(health.router)
    app.include_router(tasks.router, prefix=settings.api_prefix)
    return app


app = create_app()
