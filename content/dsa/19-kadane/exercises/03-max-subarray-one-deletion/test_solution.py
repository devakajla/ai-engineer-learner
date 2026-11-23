import random
from solution import max_sum_one_deletion


def brute(nums):
    best = None
    for i in range(len(nums)):
        for j in range(i, len(nums)):
            part = nums[i:j + 1]
            options = [sum(part)]
            if len(part) > 1:
                options += [sum(part) - x for x in part]
            m = max(options)
            best = m if best is None else max(best, m)
    return best


def test_examples():
    assert max_sum_one_deletion([1, -2, 0, 3]) == 4
    assert max_sum_one_deletion([-1, -1, -1, -1]) == -1


def test_edges():
    assert max_sum_one_deletion([1, -2, -2, 3]) == 3
    assert max_sum_one_deletion([5]) == 5
    assert max_sum_one_deletion([-4, -2]) == -2, "cannot delete the only element"
    assert max_sum_one_deletion([2, -1, 2]) == 4


def test_random():
    rng = random.Random(3)
    for _ in range(300):
        nums = [rng.randint(-6, 6) for _ in range(rng.randint(1, 9))]
        assert max_sum_one_deletion(nums) == brute(nums), f"{nums}"
