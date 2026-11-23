from solution import parse_verdict


def test_plain_and_wrapped():
    assert parse_verdict('{"score": 4, "reason": "ok"}') == {"score": 4, "reason": "ok"}
    assert parse_verdict('Sure! {"score": 4, "reason": "ok"} Done.') == {"score": 4, "reason": "ok"}


def test_missing_reason():
    assert parse_verdict('{"score": 3}') == {"score": 3, "reason": ""}
    assert parse_verdict('{"score": 3, "reason": 5}') == {"score": 3, "reason": ""}


def test_bad_scores():
    for bad in ['{"score": 9}', '{"score": 0}', '{"score": 4.0}', '{"score": "4"}', '{"score": true}', '{"reason": "x"}']:
        assert parse_verdict(bad) is None, bad


def test_not_json():
    assert parse_verdict("no json here") is None
    assert parse_verdict("{broken") is None
    assert parse_verdict("} {") is None
    assert parse_verdict("") is None


def test_not_a_dict():
    assert parse_verdict("[1, 2] and {x}") is None
