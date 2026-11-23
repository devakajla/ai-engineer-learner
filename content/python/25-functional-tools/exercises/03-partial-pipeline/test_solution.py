from solution import compose, make_cleaner, running_max


def test_compose_order():
    assert compose(str.strip, str.upper)("  hi ") == "HI"
    assert compose(lambda x: x + 1, lambda x: x * 10)(1) == 20, "left to right"
    assert compose()(5) == 5


def test_cleaner():
    clean = make_cleaner()
    assert clean("  Hello   World  ") == "hello-world"
    assert clean("A Very Long Title For A Blog Post") == "a-very-long-title-fo"


def test_running_max():
    assert running_max([3, 1, 4, 1, 5]) == [3, 3, 4, 4, 5]
    assert running_max([]) == []
