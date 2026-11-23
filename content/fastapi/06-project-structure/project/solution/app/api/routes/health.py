from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """Liveness check used by load balancers and monitoring."""
    return {"status": "ok", "app": settings.app_name}
