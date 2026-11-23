from solution import check_tool_path


def test_perfect_path():
    assert check_tool_path(["search", "summarize"], ["search", "summarize"]) == {
        "all_called": True, "in_order": True, "extra": []}


def test_extra_calls_in_between():
    assert check_tool_path(["search", "summarize"], ["search", "fetch", "summarize"]) == {
        "all_called": True, "in_order": True, "extra": ["fetch"]}


def test_wrong_order():
    assert check_tool_path(["search", "summarize"], ["summarize", "search"]) == {
        "all_called": True, "in_order": False, "extra": []}


def test_missing_tool():
    out = check_tool_path(["search", "summarize"], ["search"])
    assert out == {"all_called": False, "in_order": False, "extra": []}


def test_extra_is_unique_and_ordered():
    out = check_tool_path(["a"], ["x", "a", "y", "x", "y", "z"])
    assert out["extra"] == ["x", "y", "z"]


def test_empty_expected():
    assert check_tool_path([], []) == {"all_called": True, "in_order": True, "extra": []}
    assert check_tool_path([], ["a"]) == {"all_called": True, "in_order": True, "extra": ["a"]}


def test_repeated_expected_names():
    assert check_tool_path(["a", "b", "a"], ["a", "b"])["in_order"] is False
    assert check_tool_path(["a", "b", "a"], ["a", "b", "x", "a"])["in_order"] is True


def test_empty_actual():
    assert check_tool_path(["a"], []) == {"all_called": False, "in_order": False, "extra": []}
