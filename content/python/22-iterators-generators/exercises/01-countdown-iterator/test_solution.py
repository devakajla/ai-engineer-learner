import inspect

from solution import Countdown, countdown


def test_class():
    assert list(Countdown(3)) == [3, 2, 1]
    assert list(Countdown(0)) == [] and list(Countdown(-2)) == []


def test_class_is_one_shot():
    c = Countdown(2)
    assert iter(c) is c, "__iter__ of an iterator returns self"
    assert list(c) == [2, 1]
    assert list(c) == []


def test_generator():
    assert inspect.isgeneratorfunction(countdown), "use yield"
    assert list(countdown(3)) == [3, 2, 1]
    assert list(countdown(0)) == []
