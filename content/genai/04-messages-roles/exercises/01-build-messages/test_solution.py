from solution import build_messages


def test_examples():
    assert build_messages("Be brief.", "Hi") == [
        {"role": "system", "content": "Be brief."},
        {"role": "user", "content": "Hi"},
    ]
    assert build_messages("", "Hi") == [{"role": "user", "content": "Hi"}]


def test_none_system():
    assert build_messages(None, "Hello") == [{"role": "user", "content": "Hello"}], "None means no system message"


def test_order_and_content():
    result = build_messages("S", "U")
    assert result[0]["role"] == "system", "the system message goes first"
    assert result[1]["role"] == "user"
    assert len(result) == 2
