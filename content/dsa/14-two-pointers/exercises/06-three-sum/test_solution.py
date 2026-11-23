import random
from itertools import combinations
from solution import three_sum


def brute(nums):
    return sorted(set(tuple(sorted(c)) for c in combinations(nums, 3) if sum(c) == 0))


def test_examples():
    assert three_sum([-1, 0, 1, 2, -1, -4]) == [[-1, -1, 2], [-1, 0, 1]]
    assert three_sum([0, 0, 0, 0]) == [[0, 0, 0]]


def test_edges():
    assert three_sum([]) == []
    assert three_sum([0, 1]) == []
    assert three_sum([1, 2, 3]) == []
    assert three_sum([-2, 0, 1, 1, 2]) == [[-2, 0, 2], [-2, 1, 1]]


def test_random_against_brute_force():
    rng = random.Random(6)
    for _ in range(250):
        nums = [rng.randint(-5, 5) for _ in range(rng.randint(0, 9))]
        want = [list(t) for t in brute(nums)]
        assert three_sum(list(nums)) == want, f"{nums}: expected {want}"


def test_big_input_is_fast():
    nums = [(i * 7919) % 2001 - 1000 for i in range(1500)]
    three_sum(nums)
