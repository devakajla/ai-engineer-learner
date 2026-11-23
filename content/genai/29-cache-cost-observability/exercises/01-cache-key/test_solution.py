from solution import cache_key

MSG = [{"role": "user", "content": "hi"}]


def test_same_request_same_key():
    assert cache_key("m", MSG, 0) == cache_key("m", [{"content": "hi", "role": "user"}], 0)


def test_length_and_type():
    key = cache_key("m", MSG, 0)
    assert isinstance(key, str) and len(key) == 16


def test_anything_different_changes_key():
    base = cache_key("m", MSG, 0)
    assert cache_key("other", MSG, 0) != base
    assert cache_key("m", MSG, 0.5) != base
    assert cache_key("m", [{"role": "user", "content": "hello"}], 0) != base
    assert cache_key("m", MSG + MSG, 0) != base


def test_stable_value():
    assert cache_key("m", MSG, 0) == cache_key("m", MSG, 0)
