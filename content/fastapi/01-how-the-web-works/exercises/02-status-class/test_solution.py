import pytest

from solution import status_class


def test_classes():
    assert status_class(100) == "informational"
    assert status_class(200) == "success"
    assert status_class(204) == "success"
    assert status_class(301) == "redirect"
    assert status_class(401) == "client_error"
    assert status_class(422) == "client_error"
    assert status_class(500) == "server_error"
    assert status_class(599) == "server_error"


def test_out_of_range():
    for bad in (99, 600, 700, 0, -1):
        with pytest.raises(ValueError):
            status_class(bad)
