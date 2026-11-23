from solution import placeholders


def test_examples():
    assert placeholders("Hi {name}, you are {age}.") == ["name", "age"]
    assert placeholders("{a} and {b} and {a}") == ["a", "b"]
    assert placeholders("No holes here") == []


def test_edges():
    assert placeholders("") == []
    assert placeholders("{x}") == ["x"]
    assert placeholders('JSON {{"a": 1}} and {x}') == ["x"], "doubled braces are not placeholders"
    assert placeholders("{b}{a}{b}{c}") == ["b", "a", "c"], "keep first-seen order"
