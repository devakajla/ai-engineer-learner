from solution import unsupported

TRUSTED = {"Paris is in France", "2 + 2 = 4"}


def test_examples():
    assert unsupported(["Paris is in France", "Paris is in Spain"], TRUSTED) == ["Paris is in Spain"]
    assert unsupported(["2 + 2 = 4"], TRUSTED) == []


def test_edges():
    assert unsupported([], TRUSTED) == []
    assert unsupported(["a", "b"], set()) == ["a", "b"]
    assert unsupported(["b", "a", "b"], ["a"]) == ["b", "b"], "keep order and repeats; trusted can be a list"
