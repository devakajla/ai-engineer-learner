from solution import add_turn


def test_example():
    h = [{"role": "user", "content": "Hi"}]
    result = add_turn(h, "assistant", "Hello!")
    assert result == [
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello!"},
    ]


def test_original_is_not_changed():
    h = [{"role": "user", "content": "Hi"}]
    add_turn(h, "assistant", "Hello!")
    assert len(h) == 1, "do not change the list that was passed in (do not use append on it)"


def test_empty_history_and_returns_new_list():
    h = []
    result = add_turn(h, "user", "Hi")
    assert result == [{"role": "user", "content": "Hi"}]
    assert h == [], "the empty input list must stay empty"
    assert result is not h
