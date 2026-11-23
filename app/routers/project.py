"""The running project: checkpoint tests against the learner's own folder + Claude review."""

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.dialects.sqlite import insert

from app.config import default_project_dir
from app.content import get_lesson
from app.db import AsyncSession, SessionLocal, get_session
from app.models import ProjectCheck, Setting
from app.routers.settings import get_ai_settings
from app.services import claude
from app.services.project_files import snapshot
from app.services.runner import RunResult, run_project_tests

router = APIRouter(prefix="/api")


def _key(track_id: str) -> str:
    return f"project_dir.{track_id}"


async def get_project_dir(session: AsyncSession, track_id: str) -> str:
    row = await session.get(Setting, _key(track_id))
    return row.value if row else default_project_dir(track_id)


class ProjectDirIn(BaseModel):
    project_dir: str = Field(min_length=1, max_length=1000)


@router.put("/settings/project-dir/{track_id}")
async def set_project_dir(track_id: str, body: ProjectDirIn, session: AsyncSession = Depends(get_session)):
    value = str(Path(body.project_dir).expanduser())
    stmt = insert(Setting).values(key=_key(track_id), value=value)
    await session.execute(stmt.on_conflict_do_update(index_elements=["key"], set_={"value": value}))
    await session.commit()
    return {"project_dir": value}


class CheckOut(BaseModel):
    check_id: int
    passed: bool
    summary: str
    output: str
    seconds: float
    project_dir: str
    failures: list[dict] = []


@router.post("/project/{track_id}/{slug}/check", response_model=CheckOut)
async def check_step(track_id: str, slug: str, session: AsyncSession = Depends(get_session)):
    lesson = get_lesson(track_id, slug)
    if not lesson or not lesson.project or not lesson.project.test_file:
        raise HTTPException(404, "This lesson has no project checkpoint")
    project_dir = await get_project_dir(session, track_id)
    result = await run_project_tests(Path(project_dir), lesson.project.test_file)
    row = ProjectCheck(
        lesson_id=lesson.ref.id,
        project_dir=project_dir,
        tests_passed=result.passed,
        tests_output=result.output or result.summary,
    )
    session.add(row)
    await session.commit()
    return CheckOut(
        check_id=row.id,
        passed=result.passed,
        summary=result.summary,
        output=result.output or result.summary,
        seconds=result.seconds,
        project_dir=project_dir,
        failures=result.failures,
    )


@router.get("/project/review/{check_id}")
async def review_step(check_id: int, session: AsyncSession = Depends(get_session)):
    row = await session.get(ProjectCheck, check_id)
    if not row:
        raise HTTPException(404, "Check not found")
    if row.verdict:  # already reviewed
        return StreamingResponse(iter([row.review]), media_type="text/plain; charset=utf-8")
    track_id, slug = row.lesson_id.split("/", 1)
    lesson = get_lesson(track_id, slug)
    if not lesson:
        raise HTTPException(404, "Lesson not found")
    result = RunResult(passed=row.tests_passed, summary="", output=row.tests_output, seconds=0)
    files = snapshot(Path(row.project_dir))
    ai = await get_ai_settings(session, "review")

    async def body():
        text = ""
        try:
            async for item in claude.project_review_stream(lesson, result, files, ai):
                if isinstance(item, claude.StreamDone):
                    text = item.text
                else:
                    yield item
        except Exception as e:  # CLI missing, not logged in, etc.
            text = f"VERDICT: UNAVAILABLE\n\nClaude review failed: `{e}`"
            yield text
        async with SessionLocal() as s:
            r = await s.get(ProjectCheck, check_id)
            r.review = text
            r.verdict = claude.parse_verdict(text)
            await s.commit()

    return StreamingResponse(body(), media_type="text/plain; charset=utf-8")
