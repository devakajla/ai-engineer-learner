from pydantic import BaseModel


class Page[T](BaseModel):
    """Standard envelope for paginated list responses."""

    items: list[T]
    total: int
    limit: int
    offset: int
