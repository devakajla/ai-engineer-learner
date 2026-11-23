import pytest

from solution import AppError, ConflictError, NotFoundError, ValidationError


def test_not_found():
    e = NotFoundError("Task", 7)
    assert str(e) == "Task 7 not found"
    assert (e.status_code, e.resource, e.resource_id) == (404, "Task", 7)
    assert e.to_dict() == {"error": "NotFoundError", "message": "Task 7 not found"}


def test_hierarchy_catchable():
    for err in (NotFoundError("A", 1), ConflictError("dup"), ValidationError("title", "required")):
        with pytest.raises(AppError):
            raise err


def test_codes():
    assert AppError.status_code == 500 and ConflictError.status_code == 409


def test_validation_error():
    e = ValidationError("title", "required")
    assert str(e) == "title: required"
    assert e.to_dict() == {"error": "ValidationError", "message": "title: required", "field": "title"}


def test_conflict_to_dict():
    assert ConflictError("email taken").to_dict() == {"error": "ConflictError", "message": "email taken"}
