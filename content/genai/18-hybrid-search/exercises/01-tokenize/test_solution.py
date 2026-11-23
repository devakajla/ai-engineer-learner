from solution import tokenize


def test_examples():
    assert tokenize("Use `DELETE /tasks/{id}`.") == ["use", "delete", "/tasks/{id}"]
    assert tokenize("Error 429: too many requests!") == ["error", "429", "too", "many", "requests"]
    assert tokenize("... ?!") == []
    assert tokenize("Send the X-API-Key header.") == ["send", "the", "x-api-key", "header"]


def test_edges():
    assert tokenize("") == []
    assert tokenize("   \n\t ") == []
    assert tokenize('("quoted")') == ["quoted"]
    assert tokenize("a.b c,d") == ["a.b", "c,d"], "only the ends are stripped"
    assert tokenize("CamelCase UPPER") == ["camelcase", "upper"]
    assert tokenize("it's") == ["it's"]
