from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import func, select

from app.content import get_lesson
from app.db import AsyncSession, SessionLocal, get_session
from app.models import ExerciseHelp, Submission
from app.routers.settings import get_ai_settings
from app.services import claude
from app.services.profile import build_profile, profile_text, save_signal, tags_text
from app.services.runner import RunResult, run_tests

router = APIRouter(prefix="/api/practice")

MAX_UPLOAD_BYTES = 200_000
MAX_CODE_BYTES = 200_000
WALKTHROUGH_MIN_FAILS = 3  # failed test runs on the exercise before the walkthrough unlocks
WALKTHROUGH_MIN_LEVEL = 3  # and Dev must have seen this Coach hint level


class RunOut(BaseModel):
    submission_id: int
    passed: bool
    summary: str
    output: str
    seconds: float
    failures: list[dict] = []


def _find(owner: str, slug: str, exercise_id: str):
    lesson = get_lesson(owner, slug)
    exercise = next((e for e in lesson.exercises if e.id == exercise_id), None) if lesson else None
    if not exercise:
        raise HTTPException(404, "Exercise not found")
    return lesson, exercise


@router.post("/{owner}/{slug}/{exercise_id}", response_model=RunOut)
async def submit(
    owner: str,
    slug: str,
    exercise_id: str,
    code: str = Form(""),
    file: UploadFile | None = None,
    session: AsyncSession = Depends(get_session),
):
    lesson, exercise = _find(owner, slug, exercise_id)
    if file and file.filename:
        raw = await file.read(MAX_UPLOAD_BYTES + 1)
        if len(raw) > MAX_UPLOAD_BYTES:
            raise HTTPException(413, "File too large")
        code = raw.decode("utf-8", errors="replace")
    if not code.strip():
        raise HTTPException(400, "No code submitted")

    result = await run_tests(code, exercise.dir)
    sub = Submission(
        lesson_id=lesson.ref.id,
        exercise_id=exercise.id,
        code=code,
        tests_passed=result.passed,
        tests_output=result.output or result.summary,
    )
    session.add(sub)
    await session.commit()
    return RunOut(
        submission_id=sub.id,
        passed=result.passed,
        summary=result.summary,
        output=result.output,
        seconds=result.seconds,
        failures=result.failures,
    )


@router.get("/review/{submission_id}")
async def review(submission_id: int, session: AsyncSession = Depends(get_session)):
    sub = await session.get(Submission, submission_id)
    if not sub:
        raise HTTPException(404, "Submission not found")
    if sub.verdict:  # already reviewed
        return StreamingResponse(iter([sub.review]), media_type="text/plain; charset=utf-8")
    # The same code for the same exercise gets the same review, so reuse it instead of calling Claude.
    earlier = await session.scalar(
        select(Submission)
        .where(
            Submission.lesson_id == sub.lesson_id,
            Submission.exercise_id == sub.exercise_id,
            Submission.code == sub.code,
            Submission.verdict.is_not(None),
        )
        .order_by(Submission.id.desc())
        .limit(1)
    )
    if earlier:
        sub.review, sub.verdict = earlier.review, earlier.verdict
        await session.commit()
        return StreamingResponse(iter([sub.review]), media_type="text/plain; charset=utf-8")
    owner, slug = sub.lesson_id.split("/", 1)
    lesson, exercise = _find(owner, slug, sub.exercise_id)
    result = RunResult(passed=sub.tests_passed, summary="", output=sub.tests_output, seconds=0)
    ai = await get_ai_settings(session, "review")

    async def body():
        text = ""
        try:
            async for item in claude.review_stream(lesson, exercise, sub.code, result, ai):
                if isinstance(item, claude.StreamDone):
                    text = item.text
                else:
                    yield item
        except Exception as e:  # CLI missing, not logged in, etc.
            text = f"VERDICT: UNAVAILABLE\n\nClaude review failed: `{e}`"
            yield text
        async with SessionLocal() as s:
            row = await s.get(Submission, submission_id)
            row.review = text
            row.verdict = claude.parse_verdict(text)
            await s.commit()

    return StreamingResponse(body(), media_type="text/plain; charset=utf-8")


# --- Help on an exercise: Coach hints (levels 1-3), then a walkthrough when really stuck ---------------------


async def help_state(session: AsyncSession, lesson_id: str) -> dict[str, dict]:
    """exercise id -> {coach_level, walkthrough, fails, walkthrough_ready} for one lesson."""
    out: dict[str, dict] = {}

    def item(ex: str) -> dict:
        return out.setdefault(ex, {"coach_level": 0, "walkthrough": False, "fails": 0})

    for ex, kind, level in await session.execute(
        select(ExerciseHelp.exercise_id, ExerciseHelp.kind, func.max(ExerciseHelp.level))
        .where(ExerciseHelp.lesson_id == lesson_id)
        .group_by(ExerciseHelp.exercise_id, ExerciseHelp.kind)
    ):
        if kind == "coach":
            item(ex)["coach_level"] = level
        else:
            item(ex)["walkthrough"] = True
    for ex, fails in await session.execute(
        select(Submission.exercise_id, func.count())
        .where(Submission.lesson_id == lesson_id, Submission.tests_passed.is_(False))
        .group_by(Submission.exercise_id)
    ):
        item(ex)["fails"] = fails
    for it in out.values():
        it["walkthrough_ready"] = it["fails"] >= WALKTHROUGH_MIN_FAILS and it["coach_level"] >= WALKTHROUGH_MIN_LEVEL
    return out


def _parts(exercise) -> tuple[str, str]:
    solution = exercise.dir / "solution.py"
    return exercise.starter, solution.read_text() if solution.exists() else ""


async def _stream_help(source: str, stream, fallback: str):
    """Pass Claude's text through, then save its TOPIC line as a weak-spot signal."""
    text = ""
    try:
        async for item in stream:
            if isinstance(item, claude.StreamDone):
                text = item.text
            else:
                yield item
    except Exception as e:  # CLI missing, not logged in, etc.
        yield f"{fallback}: {e}"
        return
    await save_signal(source, text)


@router.post("/{owner}/{slug}/{exercise_id}/coach")
async def coach(
    owner: str,
    slug: str,
    exercise_id: str,
    code: str = Form(""),
    output: str = Form(""),
    level: int = Form(1),
    session: AsyncSession = Depends(get_session),
):
    lesson, exercise = _find(owner, slug, exercise_id)
    if len(code.encode()) > MAX_CODE_BYTES:
        raise HTTPException(413, "Code too large")
    level = max(1, min(level, 3))
    session.add(ExerciseHelp(lesson_id=lesson.ref.id, exercise_id=exercise.id, kind="coach", level=level))
    await session.commit()
    ai = await get_ai_settings(session, "chat")
    profile = profile_text(await build_profile(session))
    starter, solution = _parts(exercise)
    stream = claude.exercise_coach_stream(
        exercise.prompt, starter, solution, code, output, level, ai, profile, tags_text()
    )
    return StreamingResponse(
        _stream_help("coach", stream, "# Coach is not available right now"), media_type="text/plain; charset=utf-8"
    )


@router.post("/{owner}/{slug}/{exercise_id}/walkthrough")
async def walkthrough(
    owner: str,
    slug: str,
    exercise_id: str,
    code: str = Form(""),
    output: str = Form(""),
    session: AsyncSession = Depends(get_session),
):
    lesson, exercise = _find(owner, slug, exercise_id)
    if len(code.encode()) > MAX_CODE_BYTES:
        raise HTTPException(413, "Code too large")
    state = (await help_state(session, lesson.ref.id)).get(exercise.id, {})
    if not state.get("walkthrough_ready"):
        raise HTTPException(
            403,
            f"The walkthrough opens after {WALKTHROUGH_MIN_FAILS} failed test runs and Coach hint level "
            f"{WALKTHROUGH_MIN_LEVEL}. Keep trying with the hints first.",
        )
    session.add(ExerciseHelp(lesson_id=lesson.ref.id, exercise_id=exercise.id, kind="walkthrough", level=0))
    await session.commit()
    ai = await get_ai_settings(session, "chat")
    profile = profile_text(await build_profile(session))
    starter, solution = _parts(exercise)
    stream = claude.walkthrough_stream(exercise.prompt, starter, solution, code, output, ai, profile, tags_text())
    return StreamingResponse(
        _stream_help("walkthrough", stream, "Walkthrough is not available right now"),
        media_type="text/plain; charset=utf-8",
    )
