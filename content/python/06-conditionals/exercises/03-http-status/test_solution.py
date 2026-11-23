from solution import status_text


def test_examples():
    assert status_text(404) == "Not found"
    assert status_text(503) == "Server error"
    assert status_text(302) == "Unknown"


def test_all_codes():
    assert status_text(200) == "OK"
    assert status_text(201) == "Created"
    assert status_text(400) == "Client error"
    assert status_text(422) == "Client error"
    assert status_text(500) == "Server error"
    assert status_text(599) == "Server error"
    assert status_text(600) == "Unknown"
    assert status_text(0) == "Unknown"
