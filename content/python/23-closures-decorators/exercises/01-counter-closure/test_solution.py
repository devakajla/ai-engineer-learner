from solution import make_counter, make_rate_checker


def test_counter():
    c = make_counter()
    assert [c(), c(), c()] == [1, 2, 3]
    d = make_counter(10, 5)
    assert [d(), d()] == [15, 20]
    assert c() == 4, "counters must be independent"


def test_rate_checker():
    allow, reset = make_rate_checker(2)
    assert [allow(), allow(), allow()] == [True, True, False]
    reset()
    assert allow() is True


def test_independent_limiters():
    a, _ = make_rate_checker(1)
    b, _ = make_rate_checker(1)
    assert a() and b() and not a()


def test_closure_used():
    c = make_counter()
    assert c.__closure__, "use a closure (inner function capturing state)"
