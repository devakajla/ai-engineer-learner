"""The fixed daily plan (content/roadmap.yaml): today's tasks, overdue list, streak, guide.

The plan never moves. A task from a past day that is not done stays "overdue".

A "practise" task (a site lesson) is done only when its gate passes:
  - quiz: best score is at least 75% (if the task has a quiz)
  - exercises: every exercise of the task has passed its tests
  - project: the project step check has passed (if the task has one)
Lessons that are not written yet, and "review" tasks, are ticked by hand.
"""

from datetime import date, datetime
from functools import lru_cache

import yaml
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import delete, func, select
from sqlalchemy.dialects.sqlite import insert

from app.config import CONTENT_DIR
from app.content import get_tracks
from app.db import AsyncSession, get_session
from app.models import ProjectCheck, QuizAttempt, RoadmapDone, Submission
from app.routers.settings import get_ai_settings
from app.services import claude

router = APIRouter(prefix="/api/roadmap")

ROADMAP_FILE = CONTENT_DIR / "roadmap.yaml"
QUIZ_PASS_PERCENT = 75
TRACK_LABELS = {"python": "Python", "fastapi": "FastAPI", "dsa": "DSA", "genai": "GenAI", "agentic": "Agentic AI"}


@lru_cache
def load_roadmap() -> dict:
    """Returns {title, start, end, days: [{date, tasks}], tasks: {task_id: task}}."""
    if not ROADMAP_FILE.exists():
        return {"title": "", "start": None, "end": None, "days": [], "tasks": {}, "labels": TRACK_LABELS}
    raw = yaml.safe_load(ROADMAP_FILE.read_text())
    labels = {**TRACK_LABELS, **raw.get("tracks", {})}
    available = {r.id: r.available for t in get_tracks().values() for r in t.lessons}
    tasks: dict[str, dict] = {}
    days = []
    for d in raw["days"]:
        out = []
        for t in d["tasks"]:
            task = {**t, "date": str(d["date"])}
            if t.get("track"):
                task["track_label"] = labels.get(t["track"], t["track"])
            if t.get("lesson"):
                task["lesson_id"] = f"{t['track']}/{t['lesson']}"
                task["available"] = available.get(task["lesson_id"], False)
            task["gated"] = bool(
                task.get("available") and (task.get("quiz") or task.get("exercise_ids") or task.get("project"))
            )
            tasks[t["id"]] = task
            out.append(task)
        days.append({"date": str(d["date"]), "tasks": out})
    return {
        "title": raw["title"], "start": str(raw["start"]), "end": str(raw["end"]),
        "days": days, "tasks": tasks, "labels": labels,
    }


class Facts:
    """What the learner has done so far, read once per request."""

    def __init__(self, marked: set[str], quiz_best: dict[str, int], solved: dict[str, set[str]], projects: set[str]):
        self.marked, self.quiz_best, self.solved, self.projects = marked, quiz_best, solved, projects


async def load_facts(session: AsyncSession) -> Facts:
    marked = set((await session.execute(select(RoadmapDone.task_id))).scalars())
    quiz_rows = await session.execute(
        select(QuizAttempt.lesson_id, func.max(QuizAttempt.score * 100.0 / QuizAttempt.total))
        .where(QuizAttempt.total > 0)
        .group_by(QuizAttempt.lesson_id)
    )
    quiz_best = {lid: int(pct) for lid, pct in quiz_rows}
    solved: dict[str, set[str]] = {}
    for lid, ex in await session.execute(
        select(Submission.lesson_id, Submission.exercise_id).where(Submission.tests_passed.is_(True)).distinct()
    ):
        solved.setdefault(lid, set()).add(ex)
    projects = set(
        (await session.execute(select(ProjectCheck.lesson_id).where(ProjectCheck.tests_passed.is_(True)).distinct())).scalars()
    )
    return Facts(marked, quiz_best, solved, projects)


def gate_of(task: dict, facts: Facts) -> dict | None:
    """The gate of a practise task, or None when the task is ticked by hand."""
    if not task["gated"]:
        return None
    lid = task["lesson_id"]
    gate: dict = {}
    if task.get("quiz"):
        best = facts.quiz_best.get(lid)
        gate["quiz"] = {"best": best, "need": QUIZ_PASS_PERCENT, "ok": best is not None and best >= QUIZ_PASS_PERCENT}
    if task.get("exercise_ids"):
        solved = len(set(task["exercise_ids"]) & facts.solved.get(lid, set()))
        gate["exercises"] = {"solved": solved, "total": len(task["exercise_ids"]), "ok": solved == len(task["exercise_ids"])}
    if task.get("project"):
        gate["project"] = {"ok": lid in facts.projects}
    return gate


def next_tab(task: dict, gate: dict) -> str:
    """Which tab of the lesson page the Start button opens: the first step that is not done."""
    first_part = not task.get("part") or task["part"][0] == 1
    started = any(g.get("best") or g.get("solved") or g.get("ok") for g in gate.values())
    if first_part and not started:
        return "theory"
    for key, tab in (("quiz", "quiz"), ("exercises", "practice"), ("project", "project")):
        if key in gate and not gate[key]["ok"]:
            return tab
    return "theory"


def is_done(task: dict, facts: Facts) -> bool:
    gate = gate_of(task, facts)
    if gate is None:
        return task["id"] in facts.marked
    return all(g["ok"] for g in gate.values())


def task_out(task: dict, facts: Facts) -> dict:
    gate = gate_of(task, facts)
    out = {**task, "done": is_done(task, facts), "gate": gate}
    if gate is not None:
        out["tab"] = next_tab(task, gate)
    return out


def streaks(days: list[dict], today: str, facts: Facts) -> tuple[int, int]:
    """(current, best). A day counts when all its tasks are done. Today may still be open."""
    run = best = 0
    for d in days:
        if d["date"] > today:
            break
        if all(is_done(t, facts) for t in d["tasks"]):
            run += 1
            best = max(best, run)
        elif d["date"] != today:
            run = 0
    return run, best


def build_view(today: str, facts: Facts) -> dict:
    plan = load_roadmap()
    days = plan["days"]
    cur, best = streaks(days, today, facts)
    overdue = [task_out(t, facts) for d in days if d["date"] < today for t in d["tasks"] if not is_done(t, facts)]
    today_day = next((d for d in days if d["date"] == today), None)
    started = bool(plan["start"]) and today >= plan["start"]
    past = [t for d in days if d["date"] <= today for t in d["tasks"]]
    return {
        "title": plan["title"],
        "today": today,
        "start": plan["start"],
        "end": plan["end"],
        "state": "empty" if not days else "before" if not started else "after" if today > plan["end"] else "running",
        "day_number": (date.fromisoformat(today) - date.fromisoformat(plan["start"])).days + 1 if started else 0,
        "total_days": len(days),
        "tasks": [task_out(t, facts) for t in (today_day["tasks"] if today_day else [])],
        "overdue": overdue,
        "streak": cur,
        "best_streak": best,
        "due_count": len(past),
        "done_count": sum(is_done(t, facts) for t in past),
        "labels": plan["labels"],
    }


@router.get("")
async def roadmap(on: str | None = None, session: AsyncSession = Depends(get_session)):
    """Today's view plus the whole schedule (every day, with gates and done flags).
    `on=YYYY-MM-DD` previews the home page as if it were that day."""
    facts = await load_facts(session)
    view = build_view(on or date.today().isoformat(), facts)
    view["days"] = [{"date": d["date"], "tasks": [task_out(t, facts) for t in d["tasks"]]} for d in load_roadmap()["days"]]
    return view


class DoneIn(BaseModel):
    done: bool


@router.put("/tasks/{task_id}")
async def mark_task(task_id: str, body: DoneIn, session: AsyncSession = Depends(get_session)):
    """Tick a task by hand. Only for review tasks and lessons that are not written yet."""
    task = load_roadmap()["tasks"].get(task_id)
    if not task:
        raise HTTPException(404, "Unknown task")
    if task["gated"]:
        raise HTTPException(409, "This task is done by passing its quiz and exercises, not by ticking it.")
    if body.done:
        await session.execute(insert(RoadmapDone).values(task_id=task_id, done_at=datetime.now()).on_conflict_do_nothing())
    else:
        await session.execute(delete(RoadmapDone).where(RoadmapDone.task_id == task_id))
    await session.commit()
    return task_out(task, await load_facts(session))


# ---- the plan guide (Haiku) ----

_guide_cache: dict[tuple, str] = {}


def plan_context(view: dict, days: list[dict]) -> str:
    """The plan state as plain text for the guide."""
    queue = view["overdue"] + [t for t in view["tasks"] if not t["done"]]

    def line(t: dict) -> str:
        label = t.get("track_label") or "Review"
        gate = ""
        if t.get("gate"):
            g = t["gate"]
            bits = []
            if "quiz" in g:
                bits.append("quiz " + (f"best {g['quiz']['best']}%" if g["quiz"]["best"] is not None else "not taken"))
            if "exercises" in g:
                bits.append(f"exercises {g['exercises']['solved']}/{g['exercises']['total']} passed")
            if "project" in g:
                bits.append("project step " + ("passed" if g["project"]["ok"] else "not passed"))
            gate = " [" + ", ".join(bits) + "]"
        return f"{t['date']} {label}: {t['title']} ({t['minutes']} min){gate}. Steps: " + "; ".join(t.get("steps", []))

    upcoming = [d for d in days if d["date"] > view["today"]][:3]
    out = [
        f"Today is {view['today']}. Day {view['day_number']} of {view['total_days']}. Streak: {view['streak']} days "
        f"(best {view['best_streak']}). Done so far: {view['done_count']} of {view['due_count']} tasks due.",
        f"Overdue tasks: {len(view['overdue'])}"
        + (f", oldest from {min(t['date'] for t in view['overdue'])}." if view["overdue"] else "."),
        "Do next (in this order):",
        *[f"- {line(t)}" for t in queue[:4]],
    ]
    if not queue:
        out.append("- nothing: every task due so far is done")
    out.append("Coming up:")
    out += [f"- {d['date']}: " + "; ".join(t["title"] for t in d["tasks"]) for d in upcoming]
    return "\n".join(out)


async def _guide_response(session: AsyncSession, prompt: str, rules: str, cache_key: tuple | None, fallback: str):
    ai = await get_ai_settings(session, "review")  # Haiku by default
    if cache_key and cache_key in _guide_cache:
        return StreamingResponse(iter([_guide_cache[cache_key]]), media_type="text/plain; charset=utf-8")

    async def body():
        text = ""
        try:
            async for item in claude.guide_stream(prompt, ai, rules):
                if isinstance(item, claude.StreamDone):
                    text = item.text
                else:
                    yield item
        except Exception:  # CLI missing, not logged in, etc.
            text = fallback
            yield text
        if text.strip() and cache_key:
            _guide_cache[cache_key] = text

    return StreamingResponse(body(), media_type="text/plain; charset=utf-8")


@router.get("/guide")
async def guide(on: str | None = None, fresh: bool = False, session: AsyncSession = Depends(get_session)):
    """A short plan briefing from Haiku: what to do now, how, and what to watch. Cached per state."""
    facts = await load_facts(session)
    view = build_view(on or date.today().isoformat(), facts)
    if view["state"] != "running":
        return StreamingResponse(iter([""]), media_type="text/plain; charset=utf-8")
    queue = view["overdue"] + [t for t in view["tasks"] if not t["done"]]
    key = (view["today"], queue[0]["id"] if queue else "", len(view["overdue"]), view["done_count"])
    if fresh:
        _guide_cache.pop(key, None)
    n = len(view["overdue"])
    fallback = (
        f"**Now:** {queue[0]['title']}.\n\n**Watch:** {n} overdue. The plan does not move. Do the oldest first."
        if queue else "**Now:** nothing left today. Rest, then check tomorrow's plan."
    )
    return await _guide_response(session, plan_context(view, load_roadmap()["days"]), claude.GUIDE_RULES, key, fallback)


class AskIn(BaseModel):
    question: str


@router.post("/ask")
async def ask(body: AskIn, on: str | None = None, session: AsyncSession = Depends(get_session)):
    """Ask Haiku a question about the plan or today's task. One answer, no history."""
    question = body.question.strip()
    if not question:
        raise HTTPException(400, "Empty question")
    facts = await load_facts(session)
    view = build_view(on or date.today().isoformat(), facts)
    prompt = f"{plan_context(view, load_roadmap()['days'])}\n\nDev's question: {question[:1000]}"
    return await _guide_response(session, prompt, claude.ASK_RULES, None, "I could not reach Claude. Try again.")
