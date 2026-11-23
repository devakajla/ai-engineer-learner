import random
from solution import min_jumps


def brute(nums):
    n = len(nums)
    INF = 10 ** 9
    best = [INF] * n
    best[-1] = 0
    for i in range(n - 2, -1, -1):
        for j in range(i + 1, min(n, i + nums[i] + 1)):
            best[i] = min(best[i], best[j] + 1)
    return best[0]


def test_examples():
    assert min_jumps([2, 3, 1, 1, 4]) == 2
    assert min_jumps([0]) == 0


def test_random():
    rng = random.Random(3)
    done = 0
    while done < 200:
        nums = [rng.randint(0, 4) for _ in range(rng.randint(1, 8))]
        if brute(nums) >= 10 ** 9:
            continue
        done += 1
        assert min_jumps(nums) == brute(nums), f"{nums}"
