from solution import allowed


def test_group_match():
    chunk = {"tenant": "acme", "groups": ["hr"]}
    assert allowed(chunk, {"tenant": "acme", "groups": ["hr", "dev"]}) is True


def test_group_miss():
    chunk = {"tenant": "acme", "groups": ["hr"]}
    assert allowed(chunk, {"tenant": "acme", "groups": ["dev"]}) is False
    assert allowed(chunk, {"tenant": "acme"}) is False


def test_open_chunk():
    assert allowed({"tenant": "acme"}, {"tenant": "acme"}) is True
    assert allowed({"tenant": "acme", "groups": []}, {"tenant": "acme", "groups": []}) is True


def test_other_tenant_always_false():
    assert allowed({"tenant": "acme"}, {"tenant": "other"}) is False
    assert allowed({"tenant": "acme", "groups": ["hr"]}, {"tenant": "other", "groups": ["hr"]}) is False
