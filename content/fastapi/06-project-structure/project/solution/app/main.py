from fastapi import FastAPI

from app.api.routes import health, tasks
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="A task-manager REST API",
    debug=settings.debug,
)

app.include_router(health.router)
app.include_router(tasks.router, prefix=settings.api_prefix)
