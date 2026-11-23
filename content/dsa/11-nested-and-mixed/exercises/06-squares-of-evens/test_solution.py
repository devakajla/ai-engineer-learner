from solution import squares_of_evens


def test_examples():
    assert squares_of_evens([1, 2, 3, 4]) == [4, 16]
    assert squares_of_evens([1, 3]) == []


def test_more():
    assert squares_of_evens([]) == []
    assert squares_of_evens([0, -2]) == [0, 4]
