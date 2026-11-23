from solution import type_name


def test_basic_types():
    assert type_name(5) == "int"
    assert type_name(2.5) == "float"
    assert type_name("hi") == "str"
    assert type_name(True) == "bool"


def test_none_and_containers():
    assert type_name(None) == "NoneType"
    assert type_name([1, 2]) == "list"
    assert type_name((1,)) == "tuple"
    assert type_name({"a": 1}) == "dict"
    assert type_name({1}) == "set"
