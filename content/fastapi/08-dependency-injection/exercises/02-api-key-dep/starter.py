from functools import lru_cache
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, status
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_key: str = "dev-key"


app = FastAPI()
