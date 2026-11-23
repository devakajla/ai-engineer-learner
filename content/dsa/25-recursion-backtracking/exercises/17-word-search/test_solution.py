import random
from solution import exist


def brute(board, word):
    rows, cols = len(board), len(board[0])
    paths = [[(r, c)] for r in range(rows) for c in range(cols)]
    for _ in range(len(word) - 1):
        nxt = []
        for p in paths:
            r, c = p[-1]
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (r + dr, c + dc)
                if 0 <= q[0] < rows and 0 <= q[1] < cols and q not in p:
                    nxt.append(p + [q])
        paths = nxt
    return any("".join(board[r][c] for r, c in p) == word for p in paths)


def test_examples():
    board = ["ABCE", "SFCS", "ADEE"]
    assert exist(board, "ABCCED") is True
    assert exist(board, "ABCB") is False


def test_edges():
    assert exist(["A"], "A") is True
    assert exist(["A"], "AA") is False, "one cell cannot be used twice"
    assert exist(["AB"], "BA") is True


def test_random():
    rng = random.Random(17)
    for _ in range(150):
        rows, cols = rng.randint(1, 3), rng.randint(1, 3)
        board = ["".join(rng.choice("ab") for _ in range(cols)) for _ in range(rows)]
        word = "".join(rng.choice("ab") for _ in range(rng.randint(1, 5)))
        assert exist(board, word) is brute(board, word), f"{board}, {word!r}"
