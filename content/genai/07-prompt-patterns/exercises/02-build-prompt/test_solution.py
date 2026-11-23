from solution import build_prompt

HEAD = "Answer only from the text between the tags. If the answer is not there, reply exactly: I don't know."


def test_example():
    expected = HEAD + "\n\n<document>\nParis is in France.\n</document>\n\nQuestion: Where is Paris?"
    assert build_prompt("Paris is in France.", "Where is Paris?") == expected


def test_strips_spaces_and_newlines():
    expected = HEAD + "\n\n<document>\nA\nB\n</document>\n\nQuestion: Why?"
    assert build_prompt("\n  A\nB  \n", "  Why?\n") == expected, "strip the document and the question"


def test_tags_on_own_lines():
    result = build_prompt("x", "y")
    lines = result.split("\n")
    assert "<document>" in lines and "</document>" in lines, "each tag must be on its own line"
    assert not result.endswith("\n"), "no new line after the question"
