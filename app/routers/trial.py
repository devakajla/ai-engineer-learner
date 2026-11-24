"""Trial room: run free Python code, get a comment-only coaching plan, ask questions, practise weak topics."""

import json

from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import delete, select

from app.content import get_lesson
from app.db import AsyncSession, SessionLocal, get_session
from app.models import Drill, WeakSignal
from app.routers.settings import get_ai_settings
from app.services import claude, drills
from app.services.profile import build_profile, profile_text, python_tags, tags_text
from app.services.runner import run_script

router = APIRouter(prefix="/api/trial")

MAX_CODE_BYTES = 200_000
DRILLS_PER_TOPIC = 4


class ScriptOut(BaseModel):
    stdout: str
    stderr: str
    seconds: float
    timed_out: bool


def _check(code: str) -> None:
    if not code.strip():
        raise HTTPException(400, "No code to run")
    if len(code.encode()) > MAX_CODE_BYTES:
        raise HTTPException(413, "Code too large")


async def _save_signal(source: str, text: str) -> None:
    """Save the TOPIC line of Claude's reply as a weak-spot signal."""
    parsed = claude.parse_topic(text, python_tags())
    if parsed:
        async with SessionLocal() as s:
            s.add(WeakSignal(source=source, tag=parsed[0], detail=parsed[1]))
            await s.commit()


@router.post("/run", response_model=ScriptOut)
async def run(code: str = Form("")):
    _check(code)
    r = await run_script(code)
    return ScriptOut(stdout=r.stdout, stderr=r.stderr, seconds=r.seconds, timed_out=r.timed_out)


@router.post("/coach")
async def coach(
    code: str = Form(""),
    output: str = Form(""),
    attempt: int = Form(1),
    session: AsyncSession = Depends(get_session),
):
    _check(code)
    ai = await get_ai_settings(session, "chat")  # teaching, so the better model
    profile = profile_text(await build_profile(session))

    async def body():
        text = ""
        try:
            async for item in claude.coach_stream(code, output, attempt, ai, profile, tags_text()):
                if isinstance(item, claude.StreamDone):
                    text = item.text
                else:
                    yield item
        except Exception as e:  # CLI missing, not logged in, etc.
            yield f"# Coach is not available right now: {e}"
            return
        await _save_signal("coach", text)

    return StreamingResponse(body(), media_type="text/plain; charset=utf-8")


class TurnIn(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatIn(BaseModel):
    message: str
    code: str = ""
    output: str = ""
    history: list[TurnIn] = []


@router.post("/chat")
async def chat(body: ChatIn, session: AsyncSession = Depends(get_session)):
    """Ask a free question about Python or the code in the editor (not the Coach plan)."""
    if not body.message.strip():
        raise HTTPException(400, "Empty question")
    if len(body.message) > 8000:
        raise HTTPException(413, "Question too long")
    ai = await get_ai_settings(session, "chat")
    history = [(t.role, t.content) for t in body.history]
    profile = profile_text(await build_profile(session))

    async def stream():
        text = ""
        try:
            async for item in claude.trial_chat_stream(
                body.message, body.code, body.output, history, ai, profile, tags_text()
            ):
                if isinstance(item, claude.StreamDone):
                    text = item.text
                else:
                    yield item
        except Exception as e:  # CLI missing, not logged in, etc.
            yield f"Chat is not available right now: `{e}`"
            return
        await _save_signal("chat", text)

    return StreamingResponse(stream(), media_type="text/plain; charset=utf-8")


@router.get("/topics")
async def topics(session: AsyncSession = Depends(get_session)):
    """The weak-spot profile, most important first."""
    return await build_profile(session)


# ---- drills -------------------------------------------------------------------------------------


class DrillOut(BaseModel):
    id: int
    tag: str
    title: str
    prompt: str
    starter: str
    calls: list[str]
    status: str


def _drill_out(d: Drill) -> DrillOut:  # never includes the solution or the expected values
    return DrillOut(
        id=d.id, tag=d.tag, title=d.title, prompt=d.prompt, starter=d.starter,
        calls=json.loads(d.calls_json), status=d.status,
    )  # fmt: skip


class MakeDrillsIn(BaseModel):
    tag: str


class CheckIn(BaseModel):
    code: str


@router.get("/drills", response_model=list[DrillOut])
async def list_drills(tag: str, session: AsyncSession = Depends(get_session)):
    rows = (await session.execute(select(Drill).where(Drill.tag == tag).order_by(Drill.id))).scalars()
    return [_drill_out(d) for d in rows]


@router.post("/drills", response_model=list[DrillOut])
async def make_drills(body: MakeDrillsIn, session: AsyncSession = Depends(get_session)):
    """Claude writes new drills for a weak topic. Open drills of that topic are replaced, solved ones are kept."""
    lesson = get_lesson("python", body.tag) if body.tag in python_tags() else None
    if not lesson:
        raise HTTPException(400, "Pick a Python lesson topic")
    profile = await build_profile(session)
    item = next((p for p in profile if p["tag"] == body.tag), None)
    ai = await get_ai_settings(session, "chat")
    try:
        text = await claude.generate_drills(lesson, item["details"] if item else [], profile_text(profile), ai)
    except Exception as e:  # CLI missing, not logged in, etc.
        raise HTTPException(502, f"Claude is not available right now: {e}") from e
    valid = []
    for raw in drills.parse_drills_json(text)[: DRILLS_PER_TOPIC + 2]:
        ok = await drills.validate(raw)
        if ok:
            valid.append(ok)
    if len(valid) < 2:
        raise HTTPException(502, "Claude's drills were not usable this time. Press Make drills again.")
    await session.execute(delete(Drill).where(Drill.tag == body.tag, Drill.status == "open"))
    rows = [
        Drill(
            tag=body.tag, title=v["title"], prompt=v["prompt"], starter=v["starter"], solution=v["solution"],
            calls_json=json.dumps(v["calls"]), expected_json=json.dumps(v["expected"]),
        )
        for v in valid[:DRILLS_PER_TOPIC]
    ]  # fmt: skip
    session.add_all(rows)
    await session.commit()
    return [_drill_out(d) for d in rows]


@router.post("/drills/{drill_id}/check")
async def check_drill(drill_id: int, body: CheckIn, session: AsyncSession = Depends(get_session)):
    _check(body.code)
    drill = await session.get(Drill, drill_id)
    if not drill:
        raise HTTPException(404, "Drill not found")
    result = await drills.check(body.code, json.loads(drill.calls_json), json.loads(drill.expected_json))
    if result["passed"] and drill.status != "done":
        drill.status = "done"
        await session.commit()
    return {**result, "status": drill.status}
