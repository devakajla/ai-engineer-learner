from solution import format_sse


def test_with_event():
    assert format_sse("Hello", "token") == "event: token\ndata: Hello\n\n"


def test_no_event():
    assert format_sse("Hello") == "data: Hello\n\n"


def test_multiline():
    assert format_sse("a\nb", "x") == "event: x\ndata: a\ndata: b\n\n"


def test_empty_text():
    assert format_sse("") == "data: \n\n"


def test_ends_with_blank_line():
    assert format_sse("x").endswith("\n\n")
