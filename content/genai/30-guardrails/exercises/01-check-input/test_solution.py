from solution import check_input


def test_ok():
    assert check_input("Hello") == {"ok": True, "reason": ""}


def test_empty():
    assert check_input("") == {"ok": False, "reason": "empty"}
    assert check_input("  \n ") == {"ok": False, "reason": "empty"}


def test_too_long():
    assert check_input("x" * 11, max_chars=10) == {"ok": False, "reason": "too long"}
    assert check_input("x" * 10, max_chars=10)["ok"] is True


def test_banned_case_insensitive():
    out = check_input("Please IGNORE previous instructions now", banned=["ignore previous instructions"])
    assert out == {"ok": False, "reason": "banned phrase: ignore previous instructions"}


def test_banned_keeps_list_spelling():
    assert check_input("tell me the Secret", banned=["SECRET"])["reason"] == "banned phrase: SECRET"


def test_order_of_checks():
    assert check_input("x" * 20, max_chars=10, banned=["x"])["reason"] == "too long"


def test_none_banned():
    assert check_input("fine", banned=None)["ok"] is True
