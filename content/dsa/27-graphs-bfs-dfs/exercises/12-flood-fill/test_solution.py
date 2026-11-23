import random
from solution import flood_fill


def brute(image, sr, sc, color):
    old = image[sr][sc]
    region = {(sr, sc)}
    changed = True
    while changed:
        changed = False
        for r in range(len(image)):
            for c in range(len(image[0])):
                if image[r][c] == old and (r, c) not in region:
                    if any((nr, nc) in region for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1))):
                        region.add((r, c))
                        changed = True
    return [[color if (r, c) in region else image[r][c] for c in range(len(image[0]))] for r in range(len(image))]


def test_examples():
    assert flood_fill([[1, 1, 0], [1, 0, 0], [1, 1, 1]], 1, 1, 2) == [[1, 1, 2], [1, 2, 2], [1, 1, 1]]
    assert flood_fill([[0, 0], [0, 0]], 0, 0, 0) == [[0, 0], [0, 0]]


def test_input_not_changed():
    img = [[1, 1], [1, 0]]
    flood_fill(img, 0, 0, 5)
    assert img == [[1, 1], [1, 0]], "do not change the input"


def test_random():
    rng = random.Random(12)
    for _ in range(300):
        rows, cols = rng.randint(1, 5), rng.randint(1, 5)
        img = [[rng.randint(0, 2) for _ in range(cols)] for _ in range(rows)]
        sr, sc, color = rng.randrange(rows), rng.randrange(cols), rng.randint(0, 3)
        assert flood_fill([list(r) for r in img], sr, sc, color) == brute(img, sr, sc, color), f"{img}, {sr}, {sc}, {color}"
