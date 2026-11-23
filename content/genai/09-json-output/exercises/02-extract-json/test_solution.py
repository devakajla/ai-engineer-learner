from solution import extract_json


def test_examples():
    assert extract_json('Sure! Here it is: {"a": 1} Hope that helps.') == {"a": 1}
    assert extract_json('```json\n{"name": "Dev"}\n```') == {"name": "Dev"}
    assert extract_json("no json here") is None
    assert extract_json("{oops}") is None


def test_edges():
    assert extract_json('{"a": 1}') == {"a": 1}
    assert extract_json('{"a": {"b": 2}}') == {"a": {"b": 2}}, "nested objects: use the LAST }"
    assert extract_json("} before {") is None, "the } comes before the {"
    assert extract_json("") is None
    assert extract_json('Result: {"a": [1, 2]} and a stray {') == {"a": [1, 2]}, "text after the last } is ignored"
