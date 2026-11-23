from solution import usage_report


def test_examples():
    usages = [
        {"prompt_tokens": 1000, "completion_tokens": 200},
        {"prompt_tokens": 3000, "completion_tokens": 800},
    ]
    assert usage_report(usages, 0.5, 1.5) == {"calls": 2, "input_tokens": 4000, "output_tokens": 1000, "cost": 0.0035}
    assert usage_report([], 0.5, 1.5) == {"calls": 0, "input_tokens": 0, "output_tokens": 0, "cost": 0.0}


def test_edges():
    one = usage_report([{"prompt_tokens": 1_000_000, "completion_tokens": 0}], 2, 10)
    assert one["cost"] == 2.0 and one["output_tokens"] == 0
    only_output = usage_report([{"prompt_tokens": 0, "completion_tokens": 500_000}], 2, 10)
    assert only_output["cost"] == 5.0
    assert usage_report([{"prompt_tokens": 123, "completion_tokens": 456}], 1, 1)["cost"] == 0.000579, "round to 6 places"


def test_input_not_changed():
    usages = [{"prompt_tokens": 1, "completion_tokens": 2}]
    usage_report(usages, 1, 1)
    assert usages == [{"prompt_tokens": 1, "completion_tokens": 2}]
