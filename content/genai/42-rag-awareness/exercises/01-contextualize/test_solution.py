from solution import contextualize


def test_both():
    assert contextualize("The limit is 100.", "Rate limits", "Free plan") == "Rate limits > Free plan\n\nThe limit is 100."


def test_one_part():
    assert contextualize("x", heading="H") == "H\n\nx"
    assert contextualize("x", title="T") == "T\n\nx"


def test_none():
    assert contextualize("Hello") == "Hello"
    assert contextualize("Hello", "", "") == "Hello"
