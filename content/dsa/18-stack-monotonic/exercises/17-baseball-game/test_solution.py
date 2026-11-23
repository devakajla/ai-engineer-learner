from solution import calc_points


def test_examples():
    assert calc_points(["5", "2", "C", "D", "+"]) == 30
    assert calc_points(["5", "-2", "4", "C", "D", "9", "+", "+"]) == 27


def test_edges():
    assert calc_points([]) == 0
    assert calc_points(["1"]) == 1
    assert calc_points(["1", "C"]) == 0
    assert calc_points(["3", "D", "D"]) == 3 + 6 + 12
