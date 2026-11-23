from solution import reverse_in_place


def check(items):
    work = list(items)
    ident = id(work)
    res = reverse_in_place(work)
    assert res is None, "return None, change the list in place"
    assert id(work) == ident
    assert work == items[::-1], f"{items}: expected {items[::-1]}, got {work}"


def test_examples():
    check([1, 2, 3, 4])
    check([1, 2, 3])


def test_edges():
    check([])
    check([9])
    check([1, 1, 2])
    check(list(range(1001)))
