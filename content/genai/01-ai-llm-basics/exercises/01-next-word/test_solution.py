from solution import next_word

TABLE = {"I": {"like": 0.6, "am": 0.4}, "like": {"tea": 0.7, "coffee": 0.3}}


def test_examples():
    assert next_word("I", TABLE) == "like"
    assert next_word("like", TABLE) == "tea"
    assert next_word("tea", TABLE) is None, "a word that is not in the table gives None"


def test_edges():
    assert next_word("x", {"x": {}}) is None, "an empty dictionary gives None"
    assert next_word("a", {"a": {"b": 0.5, "c": 0.5}}) == "b", "a tie returns the first one"
    assert next_word("a", {"a": {"b": 0.1, "c": 0.2, "d": 0.15}}) == "c"
    assert next_word("a", {"a": {"b": 0}}) == "b", "a chance of 0 is still a valid choice"
