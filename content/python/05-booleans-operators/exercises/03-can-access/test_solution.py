import itertools

from solution import can_access


def test_all_combinations():
    for admin, owner, banned in itertools.product([True, False], repeat=3):
        expected = (admin or owner) and not banned
        got = can_access(admin, owner, banned)
        assert got == expected, f"can_access({admin}, {owner}, {banned}) should be {expected}, got {got}"


def test_returns_bool():
    assert can_access(True, False, False) is True
    assert can_access(False, False, False) is False
