"""Which Claude model and effort level the app uses, separately for chat and for reviews."""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.dialects.sqlite import insert

from app.config import CLAUDE_DEFAULTS, CLAUDE_EFFORTS, CLAUDE_MODELS, CLAUDE_USES
from app.db import AsyncSession, get_session
from app.models import Setting
from app.services.claude import AISettings

router = APIRouter(prefix="/api/settings/claude")

Use = Literal["chat", "review"]


def _keys(use: str) -> tuple[str, str]:
    return f"claude.{use}.model", f"claude.{use}.effort"


async def get_ai_settings(session: AsyncSession, use: Use) -> AISettings:
    model_key, effort_key = _keys(use)
    model = await session.get(Setting, model_key)
    effort = await session.get(Setting, effort_key)
    default_model, default_effort = CLAUDE_DEFAULTS[use]
    return AISettings(
        model=model.value if model and model.value in CLAUDE_MODELS else default_model,
        effort=effort.value if effort and effort.value in CLAUDE_EFFORTS else default_effort,
    )


class Option(BaseModel):
    id: str
    label: str


class Choice(BaseModel):
    model: str
    effort: str


class AISettingsOut(BaseModel):
    chat: Choice
    review: Choice
    defaults: dict[str, Choice]
    models: list[Option]
    efforts: list[str]


class AISettingsIn(BaseModel):
    use: Use
    model: str | None = None
    effort: Literal["low", "medium", "high", "xhigh", "max"] | None = None


async def _out(session: AsyncSession) -> AISettingsOut:
    current = {use: await get_ai_settings(session, use) for use in CLAUDE_USES}
    return AISettingsOut(
        chat=Choice(model=current["chat"].model, effort=current["chat"].effort),
        review=Choice(model=current["review"].model, effort=current["review"].effort),
        defaults={use: Choice(model=m, effort=e) for use, (m, e) in CLAUDE_DEFAULTS.items()},
        models=[Option(id=k, label=v) for k, v in CLAUDE_MODELS.items()],
        efforts=CLAUDE_EFFORTS,
    )


@router.get("", response_model=AISettingsOut)
async def read(session: AsyncSession = Depends(get_session)):
    return await _out(session)


@router.put("", response_model=AISettingsOut)
async def update(body: AISettingsIn, session: AsyncSession = Depends(get_session)):
    if body.model is not None and body.model not in CLAUDE_MODELS:
        raise HTTPException(400, "Unknown model")
    for key, value in zip(_keys(body.use), (body.model, body.effort)):
        if value is None:
            continue
        stmt = insert(Setting).values(key=key, value=value)
        await session.execute(stmt.on_conflict_do_update(index_elements=["key"], set_={"value": value}))
    await session.commit()
    return await _out(session)
