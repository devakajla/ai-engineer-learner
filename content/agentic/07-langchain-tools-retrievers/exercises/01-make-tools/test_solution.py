from solution import make_tools


def by_name():
    return {t.name: t for t in make_tools()}


def test_two_tools_with_the_right_names():
    assert sorted(by_name()) == ["convert_temp", "word_count"]


def test_description_comes_from_the_docstring():
    tools = by_name()
    assert tools["convert_temp"].description == "Convert a temperature from Celsius to Fahrenheit."
    assert tools["word_count"].description == "Count the words in a text."


def test_arguments_come_from_the_type_hints():
    tools = by_name()
    assert tools["convert_temp"].args["celsius"]["type"] == "number"
    assert tools["word_count"].args["text"]["type"] == "string"


def test_tools_work():
    tools = by_name()
    assert tools["convert_temp"].invoke({"celsius": 100}) == 212.0
    assert tools["convert_temp"].invoke({"celsius": 0}) == 32.0
    assert tools["word_count"].invoke({"text": "one two  three"}) == 3
    assert tools["word_count"].invoke({"text": ""}) == 0
