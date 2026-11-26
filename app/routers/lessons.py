from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.dialects.sqlite import insert

from app.config import project_name
from app.content import LessonRef, Track, Video, get_lesson, get_tracks, neighbours
from app.db import AsyncSession, get_session
from app.models import ChatMessage, ProjectCheck, Progress, QuizAttempt, Submission
from app.routers.doubts import lesson_doubts, open_doubt_counts
from app.routers.notes import note_out
from app.routers.practice import help_state
from app.routers.project import get_project_dir
from app.services.tools_needed import tools_needed

router = APIRouter(prefix="/api")


async def progress_map(session: AsyncSession) -> dict[str, str]:
    rows = (await session.execute(select(Progress))).scalars()
    return {r.lesson_id: r.status for r in rows}


def video_out(v: Video | None) -> dict | None:
    return {"video_id": v.video_id, "title": v.title, "start": v.start, "end": v.end} if v else None


def ref_out(ref: LessonRef | None, progress: dict[str, str], doubts: dict[str, int] | None = None) -> dict | None:
    if not ref:
        return None
    return {
        "id": ref.id,
        "slug": ref.slug,
        "title": ref.title,
        "kind": ref.kind,
        "available": ref.available,
        "status": progress.get(ref.id, "not_started"),
        "doubts": (doubts or {}).get(ref.id, 0),
    }


def track_summary(track: Track, progress: dict[str, str]) -> dict:
    total = len(track.lessons)
    done = sum(progress.get(r.id) == "done" for r in track.lessons)
    next_up = next((r for r in track.lessons if r.available and progress.get(r.id) != "done"), None)
    first = next((r for r in track.lessons if r.available), None)
    return {
        "id": track.id,
        "title": track.title,
        "done": done,
        "total": total,
        "percent": round(100 * done / total) if total else 0,
        "next_up": ref_out(next_up or first, progress),
    }


@router.get("/tracks")
async def list_tracks(session: AsyncSession = Depends(get_session)):
    progress = await progress_map(session)
    return [track_summary(t, progress) for t in get_tracks().values()]


@router.get("/tracks/{track_id}")
async def track_detail(track_id: str, session: AsyncSession = Depends(get_session)):
    track = get_tracks().get(track_id)
    if not track:
        raise HTTPException(404, "Unknown track")
    progress = await progress_map(session)
    doubts = await open_doubt_counts(session)
    return {
        **track_summary(track, progress),
        "levels": [
            {"id": lv.id, "title": lv.title, "lessons": [ref_out(r, progress, doubts) for r in lv.lessons]}
            for lv in track.levels
        ],
    }


@router.get("/lessons/{track_id}/{slug}")
async def lesson_detail(track_id: str, slug: str, session: AsyncSession = Depends(get_session)):
    lesson = get_lesson(track_id, slug)
    if not lesson:
        raise HTTPException(404, "Lesson not found")
    lesson_id = lesson.ref.id
    # Opening a lesson marks it "learning". An atomic upsert, because the browser can
    # request the same lesson twice at once (React runs effects twice in dev).
    await session.execute(
        insert(Progress).values(lesson_id=lesson_id, status="learning").on_conflict_do_nothing()
    )
    await session.commit()
    row = await session.get(Progress, lesson_id)

    last_quiz = (
        await session.execute(
            select(QuizAttempt).where(QuizAttempt.lesson_id == lesson_id).order_by(QuizAttempt.id.desc()).limit(1)
        )
    ).scalar_one_or_none()
    subs = (
        await session.execute(select(Submission).where(Submission.lesson_id == lesson_id).order_by(Submission.id))
    ).scalars().all()
    solved = {s.exercise_id for s in subs if s.tests_passed}
    latest_code = {s.exercise_id: s.code for s in subs}  # later rows win
    helps = await help_state(session, lesson_id)
    chat = (
        await session.execute(select(ChatMessage).where(ChatMessage.lesson_id == lesson_id).order_by(ChatMessage.id))
    ).scalars().all()

    project = None
    if lesson.project:
        project_passed = (
            await session.execute(
                select(ProjectCheck.id)
                .where(ProjectCheck.lesson_id == lesson_id, ProjectCheck.tests_passed.is_(True))
                .limit(1)
            )
        ).first() is not None
        project = {
            "name": project_name(track_id),
            "title": lesson.project.title,
            "instructions": lesson.project.instructions,
            "has_check": lesson.project.test_file is not None,
            "passed": project_passed,
            "project_dir": await get_project_dir(session, track_id),
        }

    progress = await progress_map(session)
    prev, nxt = neighbours(lesson.ref)
    return {
        "id": lesson_id,
        "track": track_id,
        "slug": slug,
        "title": lesson.title,
        "summary": lesson.summary,
        "plan_ids": lesson.plan_ids,
        "kind": lesson.ref.kind,
        "status": row.status,
        "body": lesson.body,
        # Answers stay on the server; they are revealed only after submitting.
        "quiz": [{"q": q.q, "type": q.type, "options": q.options} for q in lesson.quiz],
        "last_quiz": {"score": last_quiz.score, "total": last_quiz.total} if last_quiz else None,
        "intro_video": video_out(lesson.intro_video),
        "exercises": [
            {
                "id": e.id,
                "title": e.title,
                "prompt": e.prompt,
                "starter": e.starter,
                "latest_code": latest_code.get(e.id),
                "solved": e.id in solved,
                "video": video_out(e.video),
                "tools": tools_needed(e),
                "help": helps.get(e.id, {"coach_level": 0, "walkthrough": False, "fails": 0, "walkthrough_ready": False}),
            }
            for e in lesson.exercises
        ],
        "project": project,
        "chat": [{"role": m.role, "content": m.content} for m in chat],
        "doubts": await lesson_doubts(session, lesson_id),
        "note": await note_out(session, lesson_id),
        "prev": ref_out(prev, progress),
        "next": ref_out(nxt, progress),
    }


class ProgressIn(BaseModel):
    status: Literal["learning", "done"]


@router.post("/progress/{track_id}/{slug}")
async def set_progress(track_id: str, slug: str, body: ProgressIn, session: AsyncSession = Depends(get_session)):
    if not get_lesson(track_id, slug):
        raise HTTPException(404, "Lesson not found")
    lesson_id = f"{track_id}/{slug}"
    stmt = insert(Progress).values(lesson_id=lesson_id, status=body.status)
    await session.execute(stmt.on_conflict_do_update(index_elements=["lesson_id"], set_={"status": body.status, "updated_at": func.now()}))
    await session.commit()
    return {"id": lesson_id, "status": body.status}
