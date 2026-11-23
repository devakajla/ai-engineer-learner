import pytest

from solution import count_ways


def test_small_values():
    assert [count_ways(n) for n in range(0, 6)] == [1, 1, 2, 4, 7, 13]


def test_prompt_examples():
    assert count_ways(3) == 4
    assert count_ways(4) == 7


def test_big_value_is_fast():
    assert count_ways(60) == 4680045560037375, "use a cache or a loop: plain recursion is far too slow"


def test_bigger_value():
    assert count_ways(300) > 10**70


def test_negative():
    with pytest.raises(ValueError):
        count_ways(-1)
