from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select

from app.content import get_lesson
from app.db import AsyncSession, SessionLocal, get_session
from app.models import Submission
from app.routers.settings import get_ai_settings
from app.services import claude
from app.services.runner import RunResult, run_tests

router = APIRouter(prefix="/api/practice")

MAX_UPLOAD_BYTES = 200_000


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
