from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Progress(Base):
    """One row per lesson. lesson_id is '<track>/<slug>'."""

    __tablename__ = "progress"
    lesson_id: Mapped[str] = mapped_column(String, primary_key=True)
    status: Mapped[str] = mapped_column(String, default="learning")  # learning | done
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lesson_id: Mapped[str] = mapped_column(String, index=True)
    score: Mapped[int] = mapped_column(Integer)
    total: Mapped[int] = mapped_column(Integer)
    answers_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Submission(Base):
    __tablename__ = "submissions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lesson_id: Mapped[str] = mapped_column(String, index=True)
    exercise_id: Mapped[str] = mapped_column(String)
    code: Mapped[str] = mapped_column(Text)
    tests_passed: Mapped[bool] = mapped_column(Boolean)
    tests_output: Mapped[str] = mapped_column(Text)
    review: Mapped[str | None] = mapped_column(Text, nullable=True)
    verdict: Mapped[str | None] = mapped_column(String, nullable=True)  # CORRECT | PARTIAL | INCORRECT
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class ChatSession(Base):
    """Maps a lesson to the Claude Code session id, so the chat continues where it left off."""

    __tablename__ = "chat_sessions"
    lesson_id: Mapped[str] = mapped_column(String, primary_key=True)
    sdk_session_id: Mapped[str] = mapped_column(String)


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lesson_id: Mapped[str] = mapped_column(String, index=True)
    role: Mapped[str] = mapped_column(String)  # user | assistant
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class ProjectCheck(Base):
    """A run of a lesson's project checkpoint tests against the learner's project folder."""

    __tablename__ = "project_checks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lesson_id: Mapped[str] = mapped_column(String, index=True)
    project_dir: Mapped[str] = mapped_column(String)
    tests_passed: Mapped[bool] = mapped_column(Boolean)
    tests_output: Mapped[str] = mapped_column(Text)
    review: Mapped[str | None] = mapped_column(Text, nullable=True)
    verdict: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Setting(Base):
    """Simple key/value settings, e.g. the learner's project folder per track."""

    __tablename__ = "settings"
    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[str] = mapped_column(Text)


class Note(Base):
    """The learner's revision note for one lesson (Markdown). Claude drafts it, the learner saves it."""

    __tablename__ = "notes"
    lesson_id: Mapped[str] = mapped_column(String, primary_key=True)
    body: Mapped[str] = mapped_column(Text)
    chat_cursor: Mapped[int] = mapped_column(Integer, default=0)  # last ChatMessage.id already covered
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class Doubt(Base):
    """A starred spot in a lesson the learner wants to revise, with a note on what was unclear."""

    __tablename__ = "doubts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lesson_id: Mapped[str] = mapped_column(String, index=True)
    location: Mapped[str] = mapped_column(String)  # e.g. "Theory › Common mistakes", "Quiz", "Practice › Hello"
    anchor: Mapped[str | None] = mapped_column(String, nullable=True)  # heading id to scroll back to
    note: Mapped[str] = mapped_column(Text)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class WeakSignal(Base):
    """A sign that Dev is weak on a Python lesson topic: a Coach press or a trial-room chat question."""

    __tablename__ = "weak_signals"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String)  # coach | chat
    tag: Mapped[str] = mapped_column(String, index=True)  # python lesson slug, or "other"
    detail: Mapped[str] = mapped_column(String, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Drill(Base):
    """A mini exercise Claude wrote for a weak topic. `solution` and `expected_json` never leave the server."""

    __tablename__ = "drills"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tag: Mapped[str] = mapped_column(String, index=True)
    title: Mapped[str] = mapped_column(String)
    prompt: Mapped[str] = mapped_column(Text)
    starter: Mapped[str] = mapped_column(Text)
    solution: Mapped[str] = mapped_column(Text)
    calls_json: Mapped[str] = mapped_column(Text)  # list[str], expressions like next_word("I", table)
    expected_json: Mapped[str] = mapped_column(Text)  # list[str], repr of what the solution returns
    status: Mapped[str] = mapped_column(String, default="open")  # open | done
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class RoadmapDone(Base):
    """A task of content/roadmap.yaml the learner marked done."""

    __tablename__ = "roadmap_done"
    task_id: Mapped[str] = mapped_column(String, primary_key=True)
    done_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
