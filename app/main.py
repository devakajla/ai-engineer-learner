"""JSON API for the Learner app. The UI lives in frontend/ (Next.js)."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import FRONTEND_ORIGINS
from app.db import init_db
from app.routers import chat, doubts, lessons, notes, practice, project, quiz, roadmap, settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Learner API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(lessons.router)
app.include_router(quiz.router)
app.include_router(practice.router)
app.include_router(chat.router)
app.include_router(project.router)
app.include_router(settings.router)
app.include_router(doubts.router)
app.include_router(notes.router)
app.include_router(roadmap.router)


@app.get("/api/health")
async def health():
    return {"ok": True}
