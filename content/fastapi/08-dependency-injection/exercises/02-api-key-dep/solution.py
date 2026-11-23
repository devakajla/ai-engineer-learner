from functools import lru_cache
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, status
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_key: str = "dev-key"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def require_api_key(
    settings: Annotated[Settings, Depends(get_settings)],
    x_api_key: Annotated[str | None, Header()] = None,
) -> None:
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


admin = APIRouter(prefix="/admin", dependencies=[Depends(require_api_key)])


@admin.get("/stats")
def stats():
    return {"tasks": 42}


app = FastAPI()
app.include_router(admin)


@app.get("/public")
def public():
    return {"ok": True}
