from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI()

USERS: list[dict] = []
