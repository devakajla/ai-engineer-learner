import random
from solution import can_complete_circuit


def brute(gas, cost):
    n = len(gas)
    for s in range(n):
        tank = 0
        ok = True
        for k in range(n):
            i = (s + k) % n
            tank += gas[i] - cost[i]
            if tank < 0:
                ok = False
                break
        if ok:
            return s
    return -1


def test_examples():
    assert can_complete_circuit([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]) == 3
    assert can_complete_circuit([2, 3, 4], [3, 4, 3]) == -1


def test_edges():
    assert can_complete_circuit([5], [4]) == 0
    assert can_complete_circuit([1], [2]) == -1


def test_random():
    rng = random.Random(5)
    for _ in range(300):
        n = rng.randint(1, 6)
        gas = [rng.randint(0, 5) for _ in range(n)]
        cost = [rng.randint(0, 5) for _ in range(n)]
        want = brute(gas, cost)
        got = can_complete_circuit(gas, cost)
        if want == -1:
            assert got == -1, f"{gas}, {cost}"
        else:
            # more than one start can work when costs are 0, so check validity
            tank = 0
            for k in range(n):
                i = (got + k) % n
                tank += gas[i] - cost[i]
                assert tank >= 0, f"{gas}, {cost}: start {got} fails"
