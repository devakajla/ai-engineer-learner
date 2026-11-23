import random
from solution import summary_ranges


def brute(nums):
    out = []
    for n in nums:
        if out and out[-1][1] == n - 1:
            out[-1][1] = n
        else:
            out.append([n, n])
    return [str(a) if a == b else f"{a}->{b}" for a, b in out]


def test_examples():
    assert summary_ranges([0, 1, 2, 4, 5, 7]) == ["0->2", "4->5", "7"]
    assert summary_ranges([]) == []


def test_edges():
    assert summary_ranges([5]) == ["5"]
    assert summary_ranges([-1, 0, 1]) == ["-1->1"]
    assert summary_ranges([1, 3, 5]) == ["1", "3", "5"]
    assert summary_ranges([1, 2]) == ["1->2"]


def test_random():
    rng = random.Random(8)
    for _ in range(300):
        nums = sorted(rng.sample(range(-5, 15), rng.randint(0, 10)))
        assert summary_ranges(nums) == brute(nums), f"{nums}"
