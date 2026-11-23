from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

USERS = {
    1: {"id": 1, "email": "dev@x.io", "name": "Dev", "password_hash": "$2b$12$abc"},
    2: {"id": 2, "email": "ana@x.io", "name": "Ana", "password_hash": "$2b$12$def"},
}
