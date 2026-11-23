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
        users = s.scalars(select(User).options(selectinload(User.tasks)).order_by(User.id)).all()
        return [
            {
                "id": u.id,
                "email": u.email,
                "open_tasks": sum(1 for t in u.tasks if not t.done),
                "latest_task": max(u.tasks, key=lambda t: t.id).title if u.tasks else None,
            }
            for u in users
        ]
