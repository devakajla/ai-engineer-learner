from solution import toy_embed

VOCAB = ["task", "delete", "weather"]


def test_examples():
    assert toy_embed("Delete the task. Delete it!", VOCAB) == [1, 2, 0]
    assert toy_embed("Sunny weather", VOCAB) == [0, 0, 1]
    assert toy_embed("", VOCAB) == [0, 0, 0]


def test_punctuation_and_case():
    assert toy_embed("TASK, task? Task!", VOCAB) == [3, 0, 0]
    assert toy_embed("tasks", VOCAB) == [0, 0, 0], "only whole words match"


def test_length_follows_vocab():
    assert toy_embed("a b c", []) == []
    assert len(toy_embed("anything at all", ["x", "y", "z", "w", "v"])) == 5
