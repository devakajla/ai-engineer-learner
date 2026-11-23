from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, RedirectResponse
from pydantic import BaseModel

app = FastAPI()

REPORT = Path(__file__).parent / "report.txt"
