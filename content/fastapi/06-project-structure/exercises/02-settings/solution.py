from fastapi import FastAPI
from pydantic_settings import BaseSettings

app = FastAPI()


class Settings(BaseSettings):
    app_name: str = "Notes"
    debug: bool = False
    max_page_size: int = 50


def get_settings() -> Settings:
    return Settings()


@app.get("/config")
def read_config():
    s = get_settings()
    return {"app_name": s.app_name, "debug": s.debug, "max_page_size": s.max_page_size}
