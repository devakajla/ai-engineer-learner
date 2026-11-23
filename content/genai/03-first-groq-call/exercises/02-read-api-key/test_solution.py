import pytest

from solution import read_api_key


def test_returns_trimmed_key():
    assert read_api_key({"GROQ_API_KEY": " gsk_abc "}) == "gsk_abc"
    assert read_api_key({"GROQ_API_KEY": "gsk_1", "OTHER": "x"}) == "gsk_1"


def test_missing_key():
    with pytest.raises(ValueError) as info:
        read_api_key({})
    assert "GROQ_API_KEY is not set" in str(info.value)


def test_blank_key():
    for blank in ["", "   "]:
        with pytest.raises(ValueError, match="GROQ_API_KEY is not set"):
            read_api_key({"GROQ_API_KEY": blank})
