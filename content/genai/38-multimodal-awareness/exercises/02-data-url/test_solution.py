import pytest

from solution import data_url


def test_basic():
    assert data_url("image/png", b"hi") == "data:image/png;base64,aGk="


def test_other():
    assert data_url("image/jpeg", b"hello") == "data:image/jpeg;base64,aGVsbG8="


def test_empty():
    with pytest.raises(ValueError, match="no data"):
        data_url("image/png", b"")
