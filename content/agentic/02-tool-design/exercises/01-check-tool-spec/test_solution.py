from solution import check_tool_spec


def make(name="get_weather", description="Get the current weather for a city.", properties=None, required=None):
    function = {"name": name, "description": description}
    if properties is not None or required is not None:
        function["parameters"] = {"type": "object", "properties": properties or {}, "required": required or []}
    return {"type": "function", "function": function}


GOOD = make(properties={"city": {"type": "string", "description": "City name"}}, required=["city"])


def test_good_tool_has_no_problems():
    assert check_tool_spec(GOOD) == []


def test_name_rules():
    msg = "name must use lowercase letters, digits and underscores only"
    assert check_tool_spec(make(name="GetWeather")) == [msg]
    assert check_tool_spec(make(name="get-weather")) == [msg]
    assert check_tool_spec(make(name="")) == [msg]
    assert check_tool_spec(make(name="get_weather_2")) == []


def test_short_description():
    msg = "description is too short (under 20 characters)"
    assert check_tool_spec(make(description="weather")) == [msg]
    assert check_tool_spec(make(description="   short   ")) == [msg]
    assert check_tool_spec(make(description="x" * 20)) == []
    assert check_tool_spec({"type": "function", "function": {"name": "a"}}) == [msg]


def test_parameter_problems_in_order():
    tool = make(properties={
        "city": {"type": "string"},
        "days": {"type": "int", "description": "How many days"},
        "units": {"description": "  "},
    })
    assert check_tool_spec(tool) == [
        "parameter city has no description",
        "parameter days has an unknown type",
        "parameter units has no description",
        "parameter units has an unknown type",
    ]


def test_required_must_exist():
    tool = make(properties={"city": {"type": "string", "description": "City"}}, required=["city", "country", "zip"])
    assert check_tool_spec(tool) == [
        "required parameter country is not in properties",
        "required parameter zip is not in properties",
    ]


def test_all_problems_come_in_order():
    tool = make(name="Bad", description="x", properties={"a": {}}, required=["b"])
    assert check_tool_spec(tool) == [
        "name must use lowercase letters, digits and underscores only",
        "description is too short (under 20 characters)",
        "parameter a has no description",
        "parameter a has an unknown type",
        "required parameter b is not in properties",
    ]


def test_all_six_types_are_known():
    props = {t: {"type": t, "description": "d"} for t in ["string", "integer", "number", "boolean", "array", "object"]}
    assert check_tool_spec(make(properties=props)) == []
