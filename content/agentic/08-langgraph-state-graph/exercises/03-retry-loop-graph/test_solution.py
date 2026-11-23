from solution import build_retry_graph

START_STATE = {"tries": 0, "ok": False, "log": []}


def test_succeeds_on_first_try():
    out = build_retry_graph(lambda n: True, 3).invoke(START_STATE)
    assert out == {"tries": 1, "ok": True, "log": ["try 1: ok"]}


def test_retries_until_it_works():
    out = build_retry_graph(lambda n: n >= 3, 5).invoke(START_STATE)
    assert out["tries"] == 3 and out["ok"] is True
    assert out["log"] == ["try 1: fail", "try 2: fail", "try 3: ok"]


def test_gives_up_at_max_tries():
    out = build_retry_graph(lambda n: False, 2).invoke(START_STATE)
    assert out["tries"] == 2 and out["ok"] is False
    assert out["log"] == ["try 1: fail", "try 2: fail"]


def test_try_once_gets_the_try_number():
    seen = []

    def spy(n):
        seen.append(n)
        return False

    build_retry_graph(spy, 3).invoke(START_STATE)
    assert seen == [1, 2, 3]
