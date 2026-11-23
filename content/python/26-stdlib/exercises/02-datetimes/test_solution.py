from datetime import UTC, datetime, timedelta

import pytest

from solution import display, is_overdue, parse_due, time_left


def test_parse_due_to_utc():
    due = parse_due("2026-11-20T18:00:00+05:30")
    assert due.isoformat() == "2026-11-20T12:30:00+00:00"
    assert due.utcoffset() == timedelta(0)


def test_parse_due_rejects_naive():
    with pytest.raises(ValueError, match="timezone"):
        parse_due("2026-11-20T18:00:00")


def test_overdue_and_time_left():
    due = datetime(2026, 11, 20, 12, 0, tzinfo=UTC)
    now = datetime(2026, 11, 18, 6, 30, tzinfo=UTC)
    assert is_overdue(due, now) is False
    assert time_left(due, now) == "2d 5h"
    later = due + timedelta(minutes=1)
    assert is_overdue(due, later) is True and time_left(due, later) == "overdue"


def test_display():
    due = parse_due("2026-11-20T18:00:00+05:30")
    assert display(due, "Asia/Kolkata") == "20 Nov 2026, 06:00 PM"
    assert display(due, "UTC") == "20 Nov 2026, 12:30 PM"
