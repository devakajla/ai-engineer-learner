from solution import rank_students


def test_examples():
    students = [
        {"name": "Dev", "score": 90},
        {"name": "Asha", "score": 90},
        {"name": "Ravi", "score": 70},
    ]
    assert rank_students(students) == ["Asha", "Dev", "Ravi"]


def test_more():
    assert rank_students([]) == []
    assert rank_students([{"name": "Z", "score": 1}]) == ["Z"]
    assert rank_students([{"name": "b", "score": 5}, {"name": "a", "score": 7}]) == ["a", "b"]
