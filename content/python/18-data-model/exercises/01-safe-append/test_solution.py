from solution import add_tag


def test_fresh_list_each_call():
    assert add_tag("a") == ["a"]
    assert add_tag("b") == ["b"], "the default list must not be shared between calls"


def test_uses_callers_list():
    mine = ["x"]
    result = add_tag("y", mine)
    assert result is mine
    assert mine == ["x", "y"]


def test_empty_list_passed_is_used():
    mine = []
    assert add_tag("z", mine) is mine, "use `is None`, not `or []` — an empty list is falsy"
