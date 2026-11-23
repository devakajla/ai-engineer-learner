from solution import call_report


def test_examples():
    assert call_report("a" * 400, 100, 4096, 0.5, 1.5) == {
        "input_tokens": 100,
        "fits": True,
        "max_cost": 0.0002,
    }
    assert call_report("a" * 400, 4000, 4096, 0.5, 1.5) == {
        "input_tokens": 100,
        "fits": False,
        "max_cost": 0.0,
    }


def test_exact_fit_is_allowed():
    report = call_report("a" * 400, 3996, 4096, 1, 1)
    assert report["fits"] is True, "using the whole window exactly is allowed"
    assert report["max_cost"] > 0


def test_empty_prompt():
    report = call_report("", 10, 100, 1, 1)
    assert report["input_tokens"] == 0
    assert report["fits"] is True


def test_cost_uses_both_prices():
    report = call_report("a" * 4000, 1000, 10000, 1.0, 2.0)
    assert report["max_cost"] == round(1000 / 1_000_000 * 1.0 + 1000 / 1_000_000 * 2.0, 6)
