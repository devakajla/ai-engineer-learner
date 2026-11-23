from solution import grade


def test_examples():
    assert grade(95) == "A"
    assert grade(80) == "B"
    assert grade(12) == "F"


def test_boundaries():
    assert grade(90) == "A", "90 is an A"
    assert grade(89) == "B", "89 is a B"
    assert grade(79) == "C", "79 is a C"
    assert grade(70) == "C", "70 is a C"
    assert grade(69) == "F", "69 is an F"
    assert grade(0) == "F"
    assert grade(100) == "A"
