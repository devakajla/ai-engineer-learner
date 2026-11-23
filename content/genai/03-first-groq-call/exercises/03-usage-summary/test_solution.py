from types import SimpleNamespace as NS

from solution import usage_summary


def make_response(prompt, completion, total):
    usage = NS(prompt_tokens=prompt, completion_tokens=completion, total_tokens=total)
    return NS(usage=usage)


def test_example():
    assert usage_summary(make_response(12, 30, 42)) == {"input": 12, "output": 30, "total": 42}


def test_zero_and_other_values():
    assert usage_summary(make_response(0, 0, 0)) == {"input": 0, "output": 0, "total": 0}
    result = usage_summary(make_response(100, 5, 105))
    assert result["input"] == 100 and result["output"] == 5 and result["total"] == 105
    assert set(result) == {"input", "output", "total"}, "use exactly these 3 keys"
