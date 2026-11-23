from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo


def parse_due(text):
    return datetime.fromisoformat(text)


def is_overdue(due, now):
    pass


def time_left(due, now):
    pass


def display(dt, tz_name):
    pass
