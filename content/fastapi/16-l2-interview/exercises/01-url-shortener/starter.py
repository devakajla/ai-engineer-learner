from fastapi import FastAPI, HTTPException, Response, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

app = FastAPI()
