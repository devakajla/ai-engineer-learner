from solution import generate

TABLE = {"I": {"like": 0.6, "am": 0.4}, "like": {"tea": 0.7, "coffee": 0.3}}


def test_examples():
    assert generate("I", TABLE, 5) == "I like tea"
    assert generate("I", TABLE, 2) == "I like"
    assert generate("tea", TABLE, 3) == "tea"


def test_edges():
    assert generate("I", TABLE, 1) == "I", "max_words=1 keeps only the start word"
    assert generate("I", TABLE, 3) == "I like tea"
    loop = {"a": {"b": 1.0}, "b": {"a": 1.0}}
    assert generate("a", loop, 5) == "a b a b a", "loops stop at max_words"
    assert generate("x", {"x": {}}, 4) == "x"
