from solution import redact_pii


def test_email_and_phone():
    assert redact_pii("Mail me at asha@example.com, or call 9876543210.") == "Mail me at [EMAIL], or call [PHONE]."


def test_not_pii():
    assert redact_pii("Order 12345 shipped @ noon") == "Order 12345 shipped @ noon"
    assert redact_pii("@home is cool") == "@home is cool"
    assert redact_pii("me@localhost") == "me@localhost"


def test_phone_formats():
    assert redact_pii("+919876543210") == "[PHONE]"
    assert redact_pii("98765-43210!") == "[PHONE]!"
    assert redact_pii("123456789") == "123456789"


def test_spacing_is_kept():
    assert redact_pii("a  b@c.io  d") == "a  [EMAIL]  d"


def test_empty_and_plain():
    assert redact_pii("") == ""
    assert redact_pii("nothing here.") == "nothing here."


def test_email_with_tail():
    assert redact_pii("write to bob@x.org!") == "write to [EMAIL]!"
