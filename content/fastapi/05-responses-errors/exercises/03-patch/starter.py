from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

PROFILE = {"name": "Dev", "bio": "Backend dev", "city": "Pune"}
