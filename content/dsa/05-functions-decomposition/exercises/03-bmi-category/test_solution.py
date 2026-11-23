from solution import bmi_category


def test_examples():
    assert bmi_category(50, 1.8) == "underweight"
    assert bmi_category(70, 1.75) == "normal"
    assert bmi_category(95, 1.75) == "obese"


def test_edges():
    assert bmi_category(80, 1.7) == "overweight"
    assert bmi_category(25, 1) == "overweight", "exactly 25 is overweight"
    assert bmi_category(18.5, 1) == "normal", "exactly 18.5 is normal"
    assert bmi_category(30, 1) == "obese", "exactly 30 is obese"
