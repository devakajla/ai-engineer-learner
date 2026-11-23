import pytest

from solution import build_params


def test_all_tasks():
    assert build_params("extract") == {"temperature": 0, "max_completion_tokens": 200}
    assert build_params("chat") == {"temperature": 0.7, "max_completion_tokens": 500}
    assert build_params("creative") == {"temperature": 1.0, "max_completion_tokens": 800}


def test_unknown_task():
    with pytest.raises(ValueError) as info:
        build_params("poem")
    assert str(info.value) == "unknown task: poem"


def test_changing_the_result_does_not_change_later_calls():
    first = build_params("chat")
    first["temperature"] = 99
    assert build_params("chat")["temperature"] == 0.7, "return a fresh dictionary each time"
