from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import DATA_DIR, DB_URL

engine = create_async_engine(DB_URL)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db() -> None:
    from app import models  # noqa: F401  (registers tables)

    DATA_DIR.mkdir(exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session():
    async with SessionLocal() as session:
        yield session


__all__ = ["AsyncSession", "Base", "SessionLocal", "get_session", "init_db"]
