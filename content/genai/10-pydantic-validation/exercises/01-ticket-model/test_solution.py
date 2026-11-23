import pytest
from pydantic import ValidationError

from solution import Ticket


def test_valid_ticket_and_defaults():
    t = Ticket(title="Login broken", priority=3)
    assert t.title == "Login broken"
    assert t.priority == 3
    assert t.tags == [], "tags should default to an empty list"


def test_priority_is_converted():
    assert Ticket(title="Slow", priority="2", tags=["perf"]).priority == 2
    assert Ticket(title="Slow", priority="2", tags=["perf"]).tags == ["perf"]


def test_priority_range():
    for bad in (0, 6, -1, 100):
        with pytest.raises(ValidationError):
            Ticket(title="x", priority=bad)
    assert Ticket(title="x", priority=1).priority == 1
    assert Ticket(title="x", priority=5).priority == 5


def test_other_invalid_values():
    with pytest.raises(ValidationError):
        Ticket(title="", priority=3)
    with pytest.raises(ValidationError):
        Ticket(title="x", priority="very high")
    with pytest.raises(ValidationError):
        Ticket(priority=3)
    with pytest.raises(ValidationError):
        Ticket(title="x", priority=3, tags="not a list")


def test_each_ticket_has_its_own_tags_list():
    a = Ticket(title="a", priority=1)
    b = Ticket(title="b", priority=1)
    a.tags.append("x")
    assert b.tags == [], "tags must not be shared between tickets"
