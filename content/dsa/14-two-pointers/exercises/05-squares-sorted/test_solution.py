import random
from solution import sorted_squares


def test_examples():
    assert sorted_squares([-4, -1, 0, 3, 10]) == [0, 1, 9, 16, 100]
    assert sorted_squares([-7, -3, 2, 3, 11]) == [4, 9, 9, 49, 121]


def test_edges():
    assert sorted_squares([]) == []
    assert sorted_squares([-5]) == [25]
    assert sorted_squares([1, 2, 3]) == [1, 4, 9], "no negatives"
    assert sorted_squares([-3, -2, -1]) == [1, 4, 9], "all negatives"
    assert sorted_squares([-2, 2]) == [4, 4]


def test_random_and_input_unchanged():
    rng = random.Random(5)
    for _ in range(200):
        nums = sorted(rng.randint(-20, 20) for _ in range(rng.randint(0, 10)))
        copy = list(nums)
        assert sorted_squares(nums) == sorted(x * x for x in copy), f"{copy}"
        assert nums == copy, "do not change the input"


def test_big_input_is_fast():
    nums = list(range(-100000, 100000))
    res = sorted_squares(nums)
    assert res[0] == 0 and res[-1] == 100000 ** 2
