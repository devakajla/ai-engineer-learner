from solution import common_items, dedupe_keep_order


class NoScan(list):
    """A list that refuses `x in lst` and `.index` / `.count` (they scan the whole list)."""

    def __contains__(self, item):
        raise AssertionError("do not use `in` on a list: it scans every item. Use a set.")

    def index(self, *args):
        raise AssertionError("do not use .index on a list")

    def count(self, *args):
        raise AssertionError("do not use .count on a list")


def test_common_basic():
    assert common_items([5, 3, 8, 1, 8], [8, 2, 5, 9]) == [5, 8]


def test_common_empty_and_none():
    assert common_items([], [1, 2]) == []
    assert common_items([1, 2], [3, 4]) == []


def test_common_distinct():
    assert common_items([1, 1, 2, 2], [2, 2, 1]) == [1, 2]


def test_common_without_list_scans():
    a = NoScan(range(0, 40_000, 2))
    b = NoScan(range(0, 40_000, 3))
    out = common_items(a, b)
    assert out == list(range(0, 40_000, 6))


def test_dedupe_basic():
    assert dedupe_keep_order([3, 1, 3, 2, 1]) == [3, 1, 2]


def test_dedupe_empty_and_strings():
    assert dedupe_keep_order([]) == []
    assert dedupe_keep_order(["b", "a", "b", "c", "a"]) == ["b", "a", "c"]


def test_dedupe_does_not_change_input():
    data = [1, 1, 2]
    dedupe_keep_order(data)
    assert data == [1, 1, 2]


def test_dedupe_without_list_scans():
    data = NoScan([n % 5000 for n in range(50_000)])
    out = dedupe_keep_order(data)
    assert out == list(range(5000))
