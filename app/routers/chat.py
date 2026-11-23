import base64
import binascii
import re
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import delete

from app.config import CHAT_IMAGES_DIR
from app.content import get_lesson
from app.db import AsyncSession, SessionLocal, get_session
from app.models import ChatMessage, ChatSession
from app.routers.settings import get_ai_settings
from app.services import claude

router = APIRouter(prefix="/api/chat")


IMAGE_TYPES = {"image/png": "png", "image/jpeg": "jpg", "image/gif": "gif", "image/webp": "webp"}
MAX_IMAGES = 4
MAX_IMAGE_BYTES = 5 * 1024 * 1024  # Claude's own limit per image is also 5 MB
IMAGE_NAME = re.compile(r"^[0-9a-f]{32}\.(png|jpg|gif|webp)$")


class ImageIn(BaseModel):
    media_type: str
    data: str = Field(max_length=MAX_IMAGE_BYTES * 4 // 3 + 16)  # base64, no "data:" prefix


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=20_000)
    images: list[ImageIn] = Field(default_factory=list, max_length=MAX_IMAGES)

def save_images(images: list[ImageIn]) -> list[str]:
    """Validates and stores the screenshots; returns their file names."""
    names = []
    CHAT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    for img in images:
        ext = IMAGE_TYPES.get(img.media_type)
        if not ext:
            raise HTTPException(422, f"Unsupported image type {img.media_type}; use png, jpeg, gif or webp")
        try:
            raw = base64.b64decode(img.data, validate=True)
        except (binascii.Error, ValueError):
            raise HTTPException(422, "Image is not valid base64")
        if len(raw) > MAX_IMAGE_BYTES:
            raise HTTPException(413, "Image is bigger than 5 MB")
        name = f"{uuid.uuid4().hex}.{ext}"
        (CHAT_IMAGES_DIR / name).write_bytes(raw)
        names.append(name)
    return names


@router.get("/image/{name}")
async def image(name: str):
    if not IMAGE_NAME.match(name):
        raise HTTPException(404, "Not found")
    path = CHAT_IMAGES_DIR / name
    if not path.is_file():
        raise HTTPException(404, "Not found")
    return FileResponse(path, headers={"Cache-Control": "private, max-age=31536000, immutable"})


@router.post("/{owner}/{slug}")
async def send(owner: str, slug: str, body: ChatIn, session: AsyncSession = Depends(get_session)):
    lesson = get_lesson(owner, slug)
    if not lesson:
        raise HTTPException(404, "Lesson not found")
    lesson_id = lesson.ref.id
    existing = await session.get(ChatSession, lesson_id)
    resume = existing.sdk_session_id if existing else None
    ai = await get_ai_settings(session, "chat")
    names = save_images(body.images)
    # Saved chat shows the screenshots as Markdown images; Claude gets the pixels themselves.
    stored = body.message + "".join(f"\n\n![screenshot](/api/chat/image/{n})" for n in names)
    session.add(ChatMessage(lesson_id=lesson_id, role="user", content=stored))
    await session.commit()

    async def stream():
        text, new_session_id = "", None
        try:
            async for item in claude.chat_stream(
                lesson, body.message, resume, ai, [(i.media_type, i.data) for i in body.images]
            ):
                if isinstance(item, claude.StreamDone):
                    text, new_session_id = item.text, item.session_id
                else:
                    yield item
        except Exception as e:
            text = f"Claude is not available right now: `{e}`"
            yield text
        async with SessionLocal() as s:
            s.add(ChatMessage(lesson_id=lesson_id, role="assistant", content=text))
            if new_session_id:
                row = await s.get(ChatSession, lesson_id)
                if row:
                    row.sdk_session_id = new_session_id
                else:
                    s.add(ChatSession(lesson_id=lesson_id, sdk_session_id=new_session_id))
            await s.commit()

    return StreamingResponse(stream(), media_type="text/plain; charset=utf-8")


@router.delete("/{owner}/{slug}")
async def clear(owner: str, slug: str, session: AsyncSession = Depends(get_session)):
    lesson_id = f"{owner}/{slug}"
    await session.execute(delete(ChatMessage).where(ChatMessage.lesson_id == lesson_id))
    await session.execute(delete(ChatSession).where(ChatSession.lesson_id == lesson_id))
    await session.commit()
    return {"ok": True}
