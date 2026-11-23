import random
from solution import left_right_diff


def test_examples():
    assert left_right_diff([10, 4, 8, 3]) == [15, 1, 11, 22]
    assert left_right_diff([1]) == [0]


def test_edges():
    assert left_right_diff([]) == []
    assert left_right_diff([-1, 2]) == [2, 1]


def test_random():
    rng = random.Random(4)
    for _ in range(200):
        nums = [rng.randint(-5, 9) for _ in range(rng.randint(0, 10))]
        want = [abs(sum(nums[:i]) - sum(nums[i + 1:])) for i in range(len(nums))]
        assert left_right_diff(nums) == want, f"{nums}"
