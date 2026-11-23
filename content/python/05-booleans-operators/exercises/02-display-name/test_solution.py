from solution import display_name


def test_examples():
    assert display_name("  Dev ") == "Dev"
    assert display_name("") == "Anonymous"
    assert display_name("   ") == "Anonymous"


def test_inner_spaces_kept():
    assert display_name(" Ada Lovelace ") == "Ada Lovelace"
