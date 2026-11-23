from solution import check_citations


def test_ok():
    assert check_citations("Use DELETE [1].", 3) == {"cited": [1], "invalid": [], "ok": True}


def test_invalid():
    assert check_citations("Use DELETE [1][7].", 3) == {"cited": [1], "invalid": [7], "ok": False}


def test_none():
    assert check_citations("No sources.", 3) == {"cited": [], "invalid": [], "ok": False}


def test_zero_is_invalid():
    out = check_citations("x [0] y [2]", 2)
    assert out["invalid"] == [0] and out["cited"] == [2] and out["ok"] is False


def test_all_valid_many():
    out = check_citations("a [2] b [1] c [2]", 2)
    assert out == {"cited": [2, 1], "invalid": [], "ok": True}
