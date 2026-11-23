from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.pool import StaticPool

engine = create_async_engine("sqlite+aiosqlite://", poolclass=StaticPool)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    qty: Mapped[int] = mapped_column(default=0)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


DbSession = Annotated[AsyncSession, Depends(get_db)]


class ItemIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    qty: int = Field(default=0, ge=0)


class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    qty: int


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/items", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
async def create_item(payload: ItemIn, db: DbSession):
    item = Item(**payload.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@app.get("/items", response_model=list[ItemOut])
async def list_items(db: DbSession):
    return (await db.scalars(select(Item).order_by(Item.id))).all()


@app.patch("/items/{item_id}/qty", response_model=ItemOut)
async def change_qty(item_id: int, delta: int, db: DbSession):
    item = await db.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if item.qty + delta < 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Not enough stock")
    item.qty += delta
    await db.commit()
    await db.refresh(item)
    return item
