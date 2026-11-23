from solution import Ticket, parse_ticket


def test_valid():
    t = parse_ticket('{"title": "Login broken", "priority": 2}')
    assert isinstance(t, Ticket)
    assert t.title == "Login broken" and t.priority == 2 and t.tags == []


def test_with_tags_and_string_priority():
    t = parse_ticket('{"title": "x", "priority": "4", "tags": ["a", "b"]}')
    assert t is not None and t.priority == 4 and t.tags == ["a", "b"]


def test_invalid_gives_none():
    assert parse_ticket('{"title": "x", "priority": 9}') is None, "priority above 5"
    assert parse_ticket("hello") is None, "not JSON"
    assert parse_ticket('{"priority": 2}') is None, "title is missing"
    assert parse_ticket("") is None
    assert parse_ticket('{"title": "x", "priority": "high"}') is None
