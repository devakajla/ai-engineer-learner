import random
from solution import solve


def brute(board):
    rows, cols = len(board), len(board[0])
    safe = {(r, c) for r in range(rows) for c in range(cols)
            if board[r][c] == "O" and (r in (0, rows - 1) or c in (0, cols - 1))}
    changed = True
    while changed:
        changed = False
        for r in range(rows):
            for c in range(cols):
                if board[r][c] == "O" and (r, c) not in safe:
                    for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                        if (nr, nc) in safe:
                            safe.add((r, c))
                            changed = True
                            break
    return ["".join("O" if (r, c) in safe else "X" for c in range(cols)) for r in range(rows)]


def test_examples():
    assert solve(["XXXX", "XOOX", "XXOX", "XOXX"]) == ["XXXX", "XXXX", "XXXX", "XOXX"]
    assert solve(["X"]) == ["X"]


def test_edges():
    assert solve(["O"]) == ["O"]
    assert solve(["XXX", "XOX", "XXX"]) == ["XXX", "XXX", "XXX"]


def test_random():
    rng = random.Random(11)
    for _ in range(300):
        rows, cols = rng.randint(1, 5), rng.randint(1, 5)
        board = ["".join(rng.choice("XO") for _ in range(cols)) for _ in range(rows)]
        assert solve(list(board)) == brute(board), f"{board}"
