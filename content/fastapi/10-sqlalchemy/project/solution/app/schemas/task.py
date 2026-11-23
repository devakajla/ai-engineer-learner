from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskCreate(BaseModel):
    """What a client may send to create a task. Server-controlled fields (id, done) are not here."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    priority: Priority = Priority.medium


class TaskUpdate(BaseModel):
    """PATCH body: every field optional; only the fields sent are changed."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    priority: Priority | None = None
    done: bool | None = None


class TaskRead(BaseModel):
    """What the API returns for a task. Reads attributes from ORM objects."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    priority: Priority
    done: bool
    created_at: datetime
