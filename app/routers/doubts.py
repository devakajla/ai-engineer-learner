"""Doubts: starred spots in a lesson, each with a note, so the learner knows what to revise later."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.content import get_lesson
from app.db import AsyncSession, get_session
from app.models import Doubt

router = APIRouter(prefix="/api/doubts")


def doubt_out(d: Doubt) -> dict:
    track, slug = d.lesson_id.split("/", 1)
    lesson = get_lesson(track, slug)
    return {
        "id": d.id,
        "lesson_id": d.lesson_id,
        "lesson_title": lesson.title if lesson else d.lesson_id,
        "track": track,
        "slug": slug,
        "location": d.location,
        "anchor": d.anchor,
        "note": d.note,
        "resolved": d.resolved,
        "created_at": d.created_at.isoformat() if d.created_at else None,
    }


async def lesson_doubts(session: AsyncSession, lesson_id: str) -> list[dict]:
    rows = (await session.execute(select(Doubt).where(Doubt.lesson_id == lesson_id).order_by(Doubt.id))).scalars()
    return [doubt_out(d) for d in rows]


async def open_doubt_counts(session: AsyncSession) -> dict[str, int]:
    counts: dict[str, int] = {}
    for lesson_id in (await session.execute(select(Doubt.lesson_id).where(Doubt.resolved.is_(False)))).scalars():
        counts[lesson_id] = counts.get(lesson_id, 0) + 1
    return counts


class DoubtIn(BaseModel):
    location: str = Field(min_length=1, max_length=200)
    anchor: str | None = Field(default=None, max_length=200)
    note: str = Field(default="", max_length=5000)


class DoubtPatch(BaseModel):
    note: str | None = Field(default=None, max_length=5000)
    resolved: bool | None = None


@router.get("")
async def list_doubts(include_resolved: bool = False, session: AsyncSession = Depends(get_session)):
    stmt = select(Doubt).order_by(Doubt.id.desc())
    if not include_resolved:
        stmt = stmt.where(Doubt.resolved.is_(False))
    return [doubt_out(d) for d in (await session.execute(stmt)).scalars()]


@router.post("/{track_id}/{slug}", status_code=201)
async def add_doubt(track_id: str, slug: str, body: DoubtIn, session: AsyncSession = Depends(get_session)):
    if not get_lesson(track_id, slug):
        raise HTTPException(404, "Lesson not found")
    row = Doubt(lesson_id=f"{track_id}/{slug}", location=body.location, anchor=body.anchor, note=body.note.strip())
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return doubt_out(row)


async def _get(session: AsyncSession, doubt_id: int) -> Doubt:
    row = await session.get(Doubt, doubt_id)
    if not row:
        raise HTTPException(404, "Doubt not found")
    return row


@router.patch("/{doubt_id}")
async def update_doubt(doubt_id: int, body: DoubtPatch, session: AsyncSession = Depends(get_session)):
    row = await _get(session, doubt_id)
    if body.note is not None:
        row.note = body.note.strip()
    if body.resolved is not None:
        row.resolved = body.resolved
    await session.commit()
    return doubt_out(row)


@router.delete("/{doubt_id}")
async def delete_doubt(doubt_id: int, session: AsyncSession = Depends(get_session)):
    await session.delete(await _get(session, doubt_id))
    await session.commit()
    return {"ok": True}
