from solution import clean_text


def test_example():
    raw = "The exam-\nple  works.\r\n\r\n\r\n\r\n12\r\nNext   page."
    assert clean_text(raw) == "The example works.\n\nNext page."


def test_keeps_step_lines():
    assert clean_text("Step 2\n7\nDone") == "Step 2\nDone"


def test_blank_lines_limited():
    assert clean_text("a\n\n\n\n\nb") == "a\n\nb"


def test_tabs_and_spaces():
    assert clean_text("  a \t b  \n   c") == "a b\nc"


def test_empty():
    assert clean_text("") == ""
    assert clean_text("  \n 5 \n") == ""
