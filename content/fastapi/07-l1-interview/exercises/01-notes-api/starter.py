from fastapi import FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel, Field

app = FastAPI()

NOTES: dict[int, dict] = {}
