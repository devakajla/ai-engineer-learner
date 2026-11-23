import math

import pytest

from solution import Temperature


def test_conversions():
    t = Temperature(100)
    assert t.fahrenheit == 212.0
    t.fahrenheit = 32
    assert math.isclose(t.celsius, 0.0, abs_tol=1e-9)


def test_classmethod():
    t = Temperature.from_fahrenheit(212)
    assert isinstance(t, Temperature) and math.isclose(t.celsius, 100.0)


def test_classmethod_respects_subclass():
    class Sub(Temperature):
        pass

    assert type(Sub.from_fahrenheit(50)) is Sub, "use cls(...) in the classmethod"


def test_validation():
    with pytest.raises(ValueError):
        Temperature(-300)
    t = Temperature(0)
    with pytest.raises(ValueError):
        t.celsius = -274
    with pytest.raises(ValueError):
        t.fahrenheit = -500
