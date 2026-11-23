"""Notes: one revision note per lesson. Claude drafts or merges it, the learner previews and saves."""

import json
import re

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse, StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from app.content import get_lesson, get_tracks
from app.db import AsyncSession, get_session
from app.models import ChatMessage, Doubt, Note, QuizAttempt
from app.routers.quiz import score_quiz
from app.routers.settings import get_ai_settings
from app.services import claude

router = APIRouter(prefix="/api/notes")

_FENCE_RE = re.compile(r"^\s*(```|~~~)")


async def latest_chat_id(session: AsyncSession, lesson_id: str) -> int:
    stmt = select(func.max(ChatMessage.id)).where(ChatMessage.lesson_id == lesson_id)
    return (await session.execute(stmt)).scalar() or 0


async def note_out(session: AsyncSession, lesson_id: str) -> dict:
    row = await session.get(Note, lesson_id)
    latest = await latest_chat_id(session, lesson_id)
    return {
        "exists": row is not None,
        "body": row.body if row else "",
        "updated_at": row.updated_at.isoformat() if row and row.updated_at else None,
        "latest_chat_id": latest,
        # Chat after the last saved note. With no note yet, any chat counts as new.
        "has_new_chat": latest > (row.chat_cursor if row else 0),
    }


class NoteIn(BaseModel):
    body: str = Field(min_length=1, max_length=60_000)
    chat_cursor: int | None = None  # last chat message the note covers; defaults to the latest one


def _shift_headings(text: str, by: int) -> str:
    """Push Markdown headings deeper by `by` levels, leaving code blocks alone."""
    out, in_fence = [], False
    for line in text.splitlines():
        if _FENCE_RE.match(line):
            in_fence = not in_fence
        elif not in_fence and line.startswith("#"):
            line = "#" * by + line
        out.append(line)
    return "\n".join(out)


@router.get("/{track_id}/export.md")  # declared before /{owner}/{slug}, which would match "export.md"
async def export_track(track_id: str, session: AsyncSession = Depends(get_session)):
    track = get_tracks().get(track_id)
    if not track:
        raise HTTPException(404, "Unknown track")
    notes = {n.lesson_id: n for n in (await session.execute(select(Note))).scalars()}
    parts = [f"# {track.title}: revision notes"]
    for lv in track.levels:
        chunks = [
            f"### {ref.title}\n\n{_shift_headings(notes[ref.id].body.strip(), 1)}"
            for ref in lv.lessons
            if ref.id in notes
        ]
        if chunks:
            parts.append(f"## {lv.title}\n\n" + "\n\n".join(chunks))
    if len(parts) == 1:
        parts.append("No notes yet.")
    return PlainTextResponse(
        "\n\n".join(parts) + "\n",
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{track_id}-notes.md"'},
    )


@router.get("/{track_id}")
async def track_notes(track_id: str, session: AsyncSession = Depends(get_session)):
    track = get_tracks().get(track_id)
    if not track:
        raise HTTPException(404, "Unknown track")
    notes = {n.lesson_id: n for n in (await session.execute(select(Note))).scalars()}

    def lesson_out(ref) -> dict:
        n = notes.get(ref.id)
        return {
            "id": ref.id,
            "slug": ref.slug,
            "title": ref.title,
            "available": ref.available,
            "note": {"body": n.body, "updated_at": n.updated_at.isoformat() if n.updated_at else None} if n else None,
        }

    return {
        "id": track.id,
        "title": track.title,
        "levels": [{"id": lv.id, "title": lv.title, "lessons": [lesson_out(r) for r in lv.lessons]} for lv in track.levels],
    }


@router.get("/{owner}/{slug}")
async def read_note(owner: str, slug: str, session: AsyncSession = Depends(get_session)):
    lesson = get_lesson(owner, slug)
    if not lesson:
        raise HTTPException(404, "Lesson not found")
    return await note_out(session, lesson.ref.id)


@router.put("/{owner}/{slug}")
async def save_note(owner: str, slug: str, body: NoteIn, session: AsyncSession = Depends(get_session)):
    lesson = get_lesson(owner, slug)
    if not lesson:
        raise HTTPException(404, "Lesson not found")
    lesson_id = lesson.ref.id
    cursor = body.chat_cursor if body.chat_cursor is not None else await latest_chat_id(session, lesson_id)
    row = await session.get(Note, lesson_id)
    if row:
        row.body, row.chat_cursor = body.body.strip(), cursor
    else:
        session.add(Note(lesson_id=lesson_id, body=body.body.strip(), chat_cursor=cursor))
    await session.commit()
    return await note_out(session, lesson_id)


@router.delete("/{owner}/{slug}")
async def delete_note(owner: str, slug: str, session: AsyncSession = Depends(get_session)):
    row = await session.get(Note, f"{owner}/{slug}")
    if row:
        await session.delete(row)
        await session.commit()
    return {"ok": True}


@router.post("/{owner}/{slug}/generate")
async def generate_note(
    owner: str,
    slug: str,
    upto: int | None = Query(default=None, description="Only use chat messages up to this id"),
    session: AsyncSession = Depends(get_session),
):
    """Stream a new or merged note. Nothing is saved here; the learner saves after the preview."""
    lesson = get_lesson(owner, slug)
    if not lesson:
        raise HTTPException(404, "Lesson not found")
    lesson_id = lesson.ref.id
    existing = await session.get(Note, lesson_id)
    cursor = existing.chat_cursor if existing else 0
    limit = upto if upto is not None else await latest_chat_id(session, lesson_id)

    chat_rows = (
        await session.execute(
            select(ChatMessage)
            .where(ChatMessage.lesson_id == lesson_id, ChatMessage.id > cursor, ChatMessage.id <= limit)
            .order_by(ChatMessage.id)
        )
    ).scalars()
    new_chat = [(m.role, m.content) for m in chat_rows]

    doubt_rows = (await session.execute(select(Doubt).where(Doubt.lesson_id == lesson_id).order_by(Doubt.id))).scalars()
    doubts = [f"[{d.location}] {d.note}".strip() if d.note else f"[{d.location}]" for d in doubt_rows]

    wrong_quiz: list[str] = []
    last_quiz = (
        await session.execute(
            select(QuizAttempt).where(QuizAttempt.lesson_id == lesson_id).order_by(QuizAttempt.id.desc()).limit(1)
        )
    ).scalar_one_or_none()
    if last_quiz and lesson.quiz:
        chosen = json.loads(last_quiz.answers_json)
        if len(chosen) == len(lesson.quiz):
            for q, ok in zip(lesson.quiz, score_quiz(lesson.quiz, chosen)):
                if not ok:
                    wrong_quiz.append(f"{q.q.strip()} (correct: {[q.options[i] for i in q.answer]}; {q.explain})")

    ai = await get_ai_settings(session, "chat")
    old_note = existing.body if existing else ""

    async def stream():
        try:
            async for item in claude.notes_stream(lesson, old_note, new_chat, doubts, wrong_quiz, ai):
                if not isinstance(item, claude.StreamDone):
                    yield item
        except Exception as e:
            yield f"Claude is not available right now: `{e}`"

    return StreamingResponse(stream(), media_type="text/plain; charset=utf-8")
