from solution import majority_answer


def test_examples():
    assert majority_answer(["Answer: 5", "answer: 5.", "Answer: 6"]) == "answer: 5"
    assert majority_answer(["a", "b", "b"]) == "b"
    assert majority_answer(["a", "b"]) == "a", "a tie returns the first one"
    assert majority_answer([]) is None


def test_cleaning_merges_answers():
    assert majority_answer(["  Yes.", "yes", "YES.", "no"]) == "yes"


def test_tie_after_cleaning():
    assert majority_answer(["B", "a", "b", "A"]) == "b", "b reached the top count first"
