from fastapi import APIRouter

from app.api.deps import SettingsDep

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(settings: SettingsDep) -> dict[str, str]:
    """Liveness check used by load balancers and monitoring."""
    return {"status": "ok", "app": settings.app_name}
