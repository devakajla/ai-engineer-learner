from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo


def parse_due(text: str) -> datetime:
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError("timezone required")
    return dt.astimezone(UTC)


def is_overdue(due: datetime, now: datetime) -> bool:
    return now > due


def time_left(due: datetime, now: datetime) -> str:
    if now >= due:
        return "overdue"
    left: timedelta = due - now
    hours = left.seconds // 3600
    return f"{left.days}d {hours}h"


def display(dt: datetime, tz_name: str) -> str:
    return dt.astimezone(ZoneInfo(tz_name)).strftime("%d %b %Y, %I:%M %p")
