from solution import sources_from_answer

HITS = [
    {"source": "tasks.md", "heading": "Delete", "text": "a"},
    {"source": "auth.md", "text": "b"},
]


def test_basic():
    assert sources_from_answer("Use DELETE [1]. Send a token [2].", HITS) == [
        {"n": 1, "source": "tasks.md", "heading": "Delete"},
        {"n": 2, "source": "auth.md", "heading": ""},
    ]


def test_out_of_range_ignored():
    assert sources_from_answer("Made up [9] and [0].", HITS) == []


def test_order_of_appearance_and_once():
    out = sources_from_answer("x [2] y [1] z [2]", HITS)
    assert [s["n"] for s in out] == [2, 1]


def test_no_citations():
    assert sources_from_answer("Nothing.", HITS) == []
