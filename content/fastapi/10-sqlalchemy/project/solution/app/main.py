from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import health, tasks
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Temporary: create missing tables at startup. Step 11 replaces this with Alembic migrations.
    Base.metadata.create_all(bind=engine)
    yield


def create_app() -> FastAPI:
    """Application factory: builds a fully wired app (handy for tests and workers)."""
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="A task-manager REST API",
        debug=settings.debug,
        lifespan=lifespan,
    )
    app.include_router(health.router)
    app.include_router(tasks.router, prefix=settings.api_prefix)
    return app


app = create_app()
