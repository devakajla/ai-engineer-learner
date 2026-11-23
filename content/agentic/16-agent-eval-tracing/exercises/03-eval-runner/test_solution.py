from solution import add_span, pass_rate, run_eval


def make_agent(script):
    """script: {input: (answer, [tool names], tokens)}"""

    def agent(text):
        answer, tools, tokens = script[text]
        trace = []
        add_span(trace, "llm", "llm", 0, 0.1, tokens=tokens)
        for name in tools:
            add_span(trace, name, "tool", 0, 0.05)
        return {"answer": answer, "trace": trace}

    return agent


CASES = [
    {"id": "refund", "input": "refund?", "must_contain": ["5 days"], "expected_tools": ["search_docs"]},
    {"id": "sum", "input": "2+3?", "must_contain": ["5"], "expected_tools": ["calc"]},
    {"id": "hi", "input": "hello", "must_contain": [], "expected_tools": []},
]


def test_passing_and_failing_cases():
    agent = make_agent({
        "refund?": ("Refunds take 5 DAYS.", ["search_docs"], 100),
        "2+3?": ("It is 6", ["calc"], 50),
        "hello": ("Hi!", [], 10),
    })
    results = run_eval(agent, CASES)
    assert [r["id"] for r in results] == ["refund", "sum", "hi"]
    assert [r["passed"] for r in results] == [True, False, True]
    assert results[1]["answer_ok"] is False and results[1]["trajectory_ok"] is True
    assert results[0] == {"id": "refund", "answer_ok": True, "trajectory_ok": True, "passed": True,
                          "steps": 1, "tokens": 100, "ms": 150}


def test_wrong_trajectory_fails_even_with_a_good_answer():
    agent = make_agent({"refund?": ("5 days", [], 10), "2+3?": ("5", ["calc"], 10), "hello": ("Hi", [], 1)})
    results = run_eval(agent, CASES)
    assert results[0]["answer_ok"] is True and results[0]["trajectory_ok"] is False and results[0]["passed"] is False


def test_mode_is_passed_to_the_trajectory_check():
    agent = make_agent({"refund?": ("5 days", ["log", "search_docs"], 1), "2+3?": ("5", ["calc"], 1), "hello": ("Hi", [], 1)})
    assert run_eval(agent, CASES)[0]["passed"] is True
    assert run_eval(agent, CASES, mode="exact")[0]["passed"] is False


def test_a_crashing_agent_is_a_failed_case_not_a_crash():
    def agent(text):
        raise RuntimeError("model down")

    results = run_eval(agent, CASES[:1])
    assert results == [{"id": "refund", "answer_ok": False, "trajectory_ok": False, "passed": False,
                        "steps": 0, "tokens": 0, "ms": 0, "error": "model down"}]


def test_pass_rate():
    assert pass_rate([{"passed": True}, {"passed": False}, {"passed": True}, {"passed": True}]) == 0.75
    assert pass_rate([{"passed": True}, {"passed": False}, {"passed": False}]) == 0.33
    assert pass_rate([]) == 0.0
