from solution import mmr

QUERY = [0.9, 0.88, 0.5]
DOCS = [[1.0, 0.95, 0.1], [0.95, 1.0, 0.1], [0.1, 0.1, 1.0]]


def test_examples():
    assert mmr(QUERY, DOCS, 2, lam=1.0) == [0, 1]
    assert mmr(QUERY, DOCS, 2, lam=0.5) == [0, 2]


def test_lam_zero_is_pure_diversity():
    assert mmr(QUERY, DOCS, 3, lam=0.0) == [0, 2, 1], "round 1: all scores 0, tie, lowest index"


def test_k_edges():
    assert mmr(QUERY, DOCS, 0) == [] and mmr(QUERY, DOCS, -1) == []
    assert mmr([], [], 3) == []
    assert sorted(mmr(QUERY, DOCS, 10)) == [0, 1, 2]
    assert mmr(QUERY, DOCS, 1) == [0], "the first pick is the most relevant"


def test_ties_lower_index_wins():
    assert mmr([0.5, 0.5, 0.5], [[1, 0, 0], [0, 1, 0], [0, 0, 1]], 3, lam=1.0) == [0, 1, 2]


def test_penalty_uses_the_most_similar_picked_doc():
    query = [0.9, 0.8, 0.8]
    sims = [
        [1.0, 0.0, 0.9],
        [0.0, 1.0, 0.0],
        [0.9, 0.0, 1.0],
    ]
    assert mmr(query, sims, 3, lam=0.5) == [0, 1, 2]
    # doc 1 penalty 0.0 -> 0.4; doc 2 penalty 0.9 -> 0.4 - 0.45 = -0.05
