import random
from solution import find_peak


def is_peak(nums, i):
    left = nums[i - 1] if i > 0 else float("-inf")
    right = nums[i + 1] if i + 1 < len(nums) else float("-inf")
    return nums[i] > left and nums[i] > right


def test_examples():
    assert find_peak([1, 2, 3, 1]) == 2
    assert find_peak([1, 2, 1, 3, 5, 6, 4]) in (1, 5)


def test_edges():
    assert find_peak([5]) == 0
    assert find_peak([1, 2]) == 1
    assert find_peak([2, 1]) == 0


def test_random():
    rng = random.Random(17)
    for _ in range(400):
        n = rng.randint(1, 12)
        nums = [rng.randint(0, 9)]
        while len(nums) < n:
            nums.append(rng.choice([v for v in range(10) if v != nums[-1]]))
        i = find_peak(nums)
        assert 0 <= i < n and is_peak(nums, i), f"{nums}: {i} is not a peak"
