from solution import extract_citations


def test_basic():
    assert extract_citations("Use DELETE [1]. You need a token [2][1].") == [1, 2]


def test_none():
    assert extract_citations("No sources here, only [a] and [].") == []
    assert extract_citations("") == []


def test_multi_digit_and_order():
    assert extract_citations("a [12] b [3] c [12]") == [12, 3]


def test_not_citations():
    assert extract_citations("[1a] [ 1 ] [-1] [1.5]") == []


def test_unclosed_bracket():
    assert extract_citations("start [ and then [2]") == [2]
    assert extract_citations("broken [1") == []
