"""What Dev is weak at: one ranked profile built from three signals, for the UI and for Claude's prompts.

Signals (last 30 days):
- Coach presses (trial room and Practice tab), trial-room chat questions and exercise walkthroughs that Claude
  tagged with a Python lesson (table weak_signals).
- Failed exercise test runs of Python lessons (table submissions).
- Solved drills lower the score of their topic (table drills).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app import db
from app.content import get_lesson, get_tracks
from app.db import AsyncSession
from app.models import Drill, Submission, WeakSignal

WINDOW_DAYS = 30
COACH_POINTS = 2
CHAT_POINTS = 1
WALKTHROUGH_POINTS = 3
SIGNAL_POINTS = {"coach": COACH_POINTS, "chat": CHAT_POINTS, "walkthrough": WALKTHROUGH_POINTS}
DRILL_RELIEF = 2
MAX_FAILS_COUNTED = 4


def python_tags() -> dict[str, str]:
    """The fixed topic names Claude must use: Python lesson slug -> title."""
    track = get_tracks().get("python")
    return {r.slug: r.title for r in track.lessons if r.available and r.kind != "interview"} if track else {}


def tag_title(tag: str) -> str:
    return python_tags().get(tag, "Other")


def tags_text() -> str:
    return "\n".join(f"{slug}: {title}" for slug, title in python_tags().items())


async def build_profile(session: AsyncSession) -> list[dict]:
    cutoff = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=WINDOW_DAYS)
    items: dict[str, dict] = {}

    def item(tag: str) -> dict:
        return items.setdefault(
            tag,
            {"tag": tag, "title": tag_title(tag), "score": 0, "coach": 0, "chat": 0, "walkthrough": 0, "failed": [],
             "drills_done": 0, "drills_total": 0, "details": [], "last": None},
        )  # fmt: skip

    signals = (await session.execute(select(WeakSignal).where(WeakSignal.created_at >= cutoff).order_by(WeakSignal.id.desc()))).scalars()
    for s in signals:
        it = item(s.tag)
        it[s.source] = it.get(s.source, 0) + 1
        it["score"] += SIGNAL_POINTS.get(s.source, CHAT_POINTS)
        if s.detail and s.detail not in it["details"] and len(it["details"]) < 3:
            it["details"].append(s.detail)
        it["last"] = it["last"] or s.created_at

    subs = (
        await session.execute(
            select(Submission).where(Submission.lesson_id.like("python/%"), Submission.created_at >= cutoff)
        )
    ).scalars()
    per_ex: dict[tuple[str, str], dict] = {}
    for sub in subs:
        e = per_ex.setdefault((sub.lesson_id, sub.exercise_id), {"fails": 0, "solved": False})
        e["fails"] += 0 if sub.tests_passed else 1
        e["solved"] = e["solved"] or sub.tests_passed
    for (lesson_id, exercise_id), e in per_ex.items():
        if not e["fails"]:
            continue
        slug = lesson_id.split("/", 1)[1]
        lesson = get_lesson("python", slug)
        title = next((x.title for x in lesson.exercises if x.id == exercise_id), exercise_id) if lesson else exercise_id
        it = item(slug)
        it["failed"].append({"exercise": title, "fails": e["fails"], "solved": e["solved"]})
        points = min(e["fails"], MAX_FAILS_COUNTED)
        it["score"] += points / 2 if e["solved"] else points

    for d in (await session.execute(select(Drill))).scalars():
        it = item(d.tag)
        it["drills_total"] += 1
        if d.status == "done":
            it["drills_done"] += 1
            it["score"] -= DRILL_RELIEF

    for it in items.values():
        it["score"] = max(0, round(it["score"], 1))
        it["last"] = it["last"].isoformat() if it["last"] else None
    return sorted(items.values(), key=lambda i: (-i["score"], i["title"]))


def profile_text(profile: list[dict], limit: int = 5) -> str:
    """A few lines for Claude's prompt. Empty string when nothing is known yet."""
    lines = []
    for it in [p for p in profile if p["score"] > 0][:limit]:
        bits = []
        if it["coach"] or it["chat"]:
            bits.append(f"stuck {it['coach']}x, asked {it['chat']}x")
        if it.get("walkthrough"):
            bits.append(f"needed a full walkthrough {it['walkthrough']}x")
        bits += [f'failed exercise "{f["exercise"]}" {f["fails"]}x' for f in it["failed"][:2]]
        if it["drills_total"]:
            bits.append(f"drills {it['drills_done']}/{it['drills_total']} done")
        if it["details"]:
            bits.append("details: " + "; ".join(it["details"]))
        lines.append(f"- {it['title']} ({it['tag']}): " + ", ".join(bits))
    return "\n".join(lines)


async def save_signal(source: str, text: str) -> None:
    """Save the TOPIC line of Claude's reply as a weak-spot signal (source: coach | chat | walkthrough)."""
    from app.services.claude import parse_topic  # late import: claude.py is heavy

    parsed = parse_topic(text, python_tags())
    if parsed:
        async with db.SessionLocal() as s:
            s.add(WeakSignal(source=source, tag=parsed[0], detail=parsed[1]))
            await s.commit()
