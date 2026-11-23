from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, RedirectResponse
from pydantic import BaseModel

app = FastAPI()

REPORT = Path(__file__).parent / "report.txt"


class Profile(BaseModel):
    id: int
    name: str
    bio: str | None = None


@app.get("/page", response_class=HTMLResponse)
def page():
    return "<h1>Hello</h1>"


@app.get("/old")
def old():
    return RedirectResponse("/new", status_code=301)


@app.get("/new", response_class=PlainTextResponse)
def new():
    return "new"


@app.get("/download")
def download():
    return FileResponse(REPORT, filename="report.txt")


@app.get("/profile", response_model=Profile, response_model_exclude_none=True)
def profile():
    return {"id": 1, "name": "Ana", "bio": None}
