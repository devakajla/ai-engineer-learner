from solution import start_simple


class Counter:
    def __init__(self, answer):
        self.answer = answer
        self.questions = []

    def __call__(self, question):
        self.questions.append(question)
        return self.answer


def long_enough(answer):
    return len(answer) >= 5


def test_good_simple_answer_skips_the_agent():
    simple, agent = Counter("Paris is it"), Counter("agent")
    assert start_simple("q", simple, agent, long_enough) == {"answer": "Paris is it", "used": "simple"}
    assert simple.questions == ["q"] and agent.questions == []


def test_weak_simple_answer_calls_the_agent_once():
    simple, agent = Counter("no"), Counter("Paris")
    assert start_simple("q", simple, agent, long_enough) == {"answer": "Paris", "used": "agent"}
    assert agent.questions == ["q"]


def test_exception_in_the_simple_path_goes_to_the_agent():
    def broken(question):
        raise RuntimeError("boom")

    agent = Counter("fallback")
    assert start_simple("q", broken, agent, long_enough) == {"answer": "fallback", "used": "agent"}


def test_the_agent_answer_is_not_checked():
    assert start_simple("q", Counter("no"), Counter("x"), long_enough)["answer"] == "x"


def test_good_enough_gets_the_simple_answer():
    seen = []

    def spy(answer):
        seen.append(answer)
        return True

    start_simple("q", Counter("abc"), Counter("zzz"), spy)
    assert seen == ["abc"]
