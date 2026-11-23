from solution import find_regressions, gate


def res(id, passed, tokens=100):
    return {"id": id, "passed": passed, "tokens": tokens}


BASE = [res("a", True), res("b", True), res("c", False), res("d", True)]


def test_find_regressions_only_lists_cases_that_passed_before_and_fail_now():
    new = [res("a", True), res("b", False), res("c", False), res("d", True)]
    assert find_regressions(BASE, new) == ["b"]


def test_a_case_that_was_already_failing_is_not_a_regression():
    new = [res("a", True), res("b", True), res("c", False), res("d", True)]
    assert find_regressions(BASE, new) == []


def test_new_cases_are_not_regressions():
    assert find_regressions(BASE, [res("zzz", False)]) == []


def test_gate_ok_when_nothing_got_worse():
    new = [res("a", True), res("b", True), res("c", True), res("d", True)]
    assert gate(BASE, new) == {"ok": True, "reasons": []}


def test_gate_blocks_a_drop_in_pass_rate_and_names_the_regressions():
    new = [res("a", False), res("b", False), res("c", False), res("d", True)]
    out = gate(BASE, new)
    assert out["ok"] is False
    assert out["reasons"] == ["pass rate fell by 0.5", "regressions: a, b"]


def test_one_regression_blocks_even_if_the_rate_is_the_same():
    new = [res("a", True), res("b", False), res("c", True), res("d", True)]
    out = gate(BASE, new)
    assert out == {"ok": False, "reasons": ["regressions: b"]}


def test_gate_blocks_token_growth():
    new = [res("a", True, 150), res("b", True, 150), res("c", False, 150), res("d", True, 150)]
    out = gate(BASE, new)
    assert out == {"ok": False, "reasons": ["token use grew by 50%"]}
    assert gate(BASE, new, max_token_growth=0.6)["ok"] is True


def test_small_drop_inside_max_drop_is_tolerated_but_a_regression_is_not():
    base = [res(str(i), True) for i in range(20)]
    new = [res(str(i), i != 0) for i in range(20)]       # 19/20 = 0.95, a drop of 0.05
    out = gate(base, new)
    assert out["reasons"] == ["regressions: 0"]
