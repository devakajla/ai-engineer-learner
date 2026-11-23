from solution import allow_request


def test_first_request():
    assert allow_request([], 100, 2, 60) == {"allowed": True, "timestamps": [100], "retry_after": 0}


def test_blocked_with_retry_after():
    out = allow_request([100, 110], 120, 2, 60)
    assert out == {"allowed": False, "timestamps": [100, 110], "retry_after": 40}


def test_old_ones_forgotten():
    out = allow_request([100, 110], 161, 2, 60)
    assert out == {"allowed": True, "timestamps": [110, 161], "retry_after": 0}


def test_boundary_exactly_window_ago_is_forgotten():
    out = allow_request([100, 110], 160, 2, 60)
    assert out["allowed"] is True and out["timestamps"] == [110, 160]


def test_limit_one():
    first = allow_request([], 0, 1, 10)
    second = allow_request(first["timestamps"], 3, 1, 10)
    assert second["allowed"] is False and second["retry_after"] == 7
    third = allow_request(second["timestamps"], 10, 1, 10)
    assert third["allowed"] is True


def test_input_not_changed():
    stamps = [100, 110]
    allow_request(stamps, 120, 3, 60)
    assert stamps == [100, 110]
