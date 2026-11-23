import pytest
from pydantic import ValidationError

from solution import SignupForm

OK = {"username": "Dev_22", "email": " Dev@X.io ", "password": "Secret123", "password_confirm": "Secret123"}


def test_valid_and_normalized():
    f = SignupForm(**OK)
    assert f.username == "dev_22" and f.email == "dev@x.io" and f.age is None


@pytest.mark.parametrize(
    "changes",
    [
        {"username": "ab"},
        {"username": "bad name"},
        {"username": "x" * 21},
        {"email": "nope"},
        {"email": "a@b@c.io"},
        {"email": "a@localhost"},
        {"password": "short1A", "password_confirm": "short1A"},
        {"password": "alllowercase1", "password_confirm": "alllowercase1"},
        {"password": "NoDigitsHere", "password_confirm": "NoDigitsHere"},
        {"password_confirm": "Different123"},
        {"age": 12},
    ],
)
def test_invalid(changes):
    with pytest.raises(ValidationError):
        SignupForm(**{**OK, **changes})


def test_mismatch_message():
    with pytest.raises(ValidationError, match="passwords do not match"):
        SignupForm(**{**OK, "password_confirm": "Other1234"})
