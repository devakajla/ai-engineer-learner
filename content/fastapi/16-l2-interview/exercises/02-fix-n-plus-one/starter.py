from fastapi import FastAPI
from sqlalchemy import ForeignKey, String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, selectinload
from sqlalchemy.pool import StaticPool

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(100))
    tasks: Mapped[list["Task"]] = relationship(back_populates="owner")


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    done: Mapped[bool] = mapped_column(default=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped[User] = relationship(back_populates="tasks")


def seed() -> None:
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        for u in range(1, 31):
            user = User(email=f"user{u}@x.io")
            user.tasks = [Task(title=f"u{u}-t{t}", done=(t % 2 == 0)) for t in range(u % 4)]
            s.add(user)
        s.commit()


seed()
app = FastAPI()


@app.get("/users")
def list_users():
    with Session(engine) as s:
        result = []
        for user in s.scalars(select(User).order_by(User.id)):
            open_count = s.scalar(select(func.count()).where(Task.owner_id == user.id, Task.done.is_(False)))
            latest = s.scalar(select(Task.title).where(Task.owner_id == user.id).order_by(Task.id.desc()).limit(1))
            result.append({"id": user.id, "email": user.email, "open_tasks": open_count, "latest_task": latest})
        return result
