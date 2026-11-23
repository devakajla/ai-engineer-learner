from solution import detect_failure


def step(tool, args=None, result="ok"):
    return {"tool": tool, "args": args or {}, "result": result}


def test_clean_trace():
    trace = [step("a"), step("b"), step("c", {"x": 1})]
    assert detect_failure(trace) == []
    assert detect_failure([]) == []


def test_loop():
    trace = [step("search", {"q": "x"}) for _ in range(3)]
    assert detect_failure(trace) == ["loop"]


def test_loop_not_in_a_row():
    trace = [step("search", {"q": "x"}), step("other"), step("search", {"q": "x"}), step("another"), step("search", {"q": "x"})]
    assert detect_failure(trace) == ["loop"]


def test_two_repeats_are_fine():
    trace = [step("search", {"q": "x"}), step("search", {"q": "x"})]
    assert detect_failure(trace) == []


def test_different_arguments_are_not_a_loop():
    trace = [step("search", {"q": str(n)}) for n in range(5)]
    assert detect_failure(trace) == []


def test_error_streak():
    trace = [step("a", {"n": 1}, "error: x"), step("b", {"n": 2}, "error: y"), step("c", {"n": 3}, "error: z")]
    assert detect_failure(trace) == ["error_streak"]


def test_errors_must_be_in_a_row():
    trace = [step("a", {"n": 1}, "error: x"), step("b", {"n": 2}, "error: y"), step("c", {"n": 3}, "fine"),
             step("d", {"n": 4}, "error: z"), step("e", {"n": 5}, "error: w")]
    assert detect_failure(trace) == []


def test_max_steps():
    trace = [step("a", {"n": n}) for n in range(4)]
    assert detect_failure(trace, max_steps=4) == ["max_steps"]
    assert detect_failure(trace, max_steps=5) == []


def test_default_max_steps_is_ten():
    assert detect_failure([step("a", {"n": n}) for n in range(10)]) == ["max_steps"]
    assert detect_failure([step("a", {"n": n}) for n in range(9)]) == []


def test_all_labels_in_order():
    trace = [step("a", {}, "error: no")] * 3
    assert detect_failure(trace, max_steps=3) == ["loop", "error_streak", "max_steps"]


def test_non_text_results_do_not_crash():
    assert detect_failure([step("a", {"n": 1}, 5), step("b", {"n": 2}, None)]) == []
