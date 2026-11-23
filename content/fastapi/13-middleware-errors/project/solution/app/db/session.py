from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

# One engine (and connection pool) per process.
engine = create_async_engine(get_settings().database_url)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


async def get_db() -> AsyncIterator[AsyncSession]:
    """One async session per request, always closed afterwards."""
    async with SessionLocal() as session:
        yield session
