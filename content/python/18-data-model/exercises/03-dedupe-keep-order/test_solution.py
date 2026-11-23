from solution import dedupe


def test_order_and_no_mutation():
    data = [3, 1, 3, 2, 1]
    assert dedupe(data) == [3, 1, 2]
    assert data == [3, 1, 3, 2, 1], "don't mutate the input"


def test_returns_new_list():
    data = [1, 2]
    assert dedupe(data) is not data


def test_edge_and_large():
    assert dedupe([]) == []
    big = list(range(100_000)) * 2
    assert dedupe(big) == list(range(100_000))
