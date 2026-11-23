from solution import content_hash


def test_whitespace_does_not_matter():
    assert content_hash("Hello  world") == content_hash("Hello\nworld") == content_hash("  Hello world ")


def test_different_text():
    assert content_hash("Hello there") != content_hash("Hello world")


def test_length_and_type():
    h = content_hash("x")
    assert isinstance(h, str) and len(h) == 16
    assert len(content_hash("")) == 16


def test_stable_value():
    assert content_hash("a") == "ca978112ca1bbdca"
