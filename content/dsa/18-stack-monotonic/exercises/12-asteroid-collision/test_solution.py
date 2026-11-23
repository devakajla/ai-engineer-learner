import random
from solution import asteroid_collision


def brute(ast):
    ast = list(ast)
    while True:
        for i in range(len(ast) - 1):
            if ast[i] > 0 and ast[i + 1] < 0:
                a, b = ast[i], ast[i + 1]
                if a > -b:
                    ast = ast[:i + 1] + ast[i + 2:]
                elif a < -b:
                    ast = ast[:i] + ast[i + 1:]
                else:
                    ast = ast[:i] + ast[i + 2:]
                break
        else:
            return ast


def test_examples():
    assert asteroid_collision([5, 10, -5]) == [5, 10]
    assert asteroid_collision([8, -8]) == []


def test_edges():
    assert asteroid_collision([]) == []
    assert asteroid_collision([10, 2, -5]) == [10]
    assert asteroid_collision([-2, -1, 1, 2]) == [-2, -1, 1, 2], "moving apart"
    assert asteroid_collision([1, -2, -2, -2]) == [-2, -2, -2]


def test_random():
    rng = random.Random(12)
    for _ in range(400):
        ast = [rng.choice([-1, 1]) * rng.randint(1, 5) for _ in range(rng.randint(0, 8))]
        assert asteroid_collision(ast) == brute(ast), f"{ast}"
