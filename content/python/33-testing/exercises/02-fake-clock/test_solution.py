import pytest

from solution import RateLimiter


class FakeClock:
    def __init__(self, start=0.0):
        self.now = start

    def __call__(self):
        return self.now


def test_allows_up_to_limit_then_blocks():
    clock = FakeClock()
    limiter = RateLimiter(2, 10, clock)
    assert [limiter.allow() for _ in range(3)] == [True, True, False]


def test_old_calls_expire_exactly_at_window_end():
    clock = FakeClock()
    limiter = RateLimiter(2, 10, clock)
    limiter.allow()
    limiter.allow()
    clock.now = 9.99
    assert limiter.allow() is False, "calls at t=0 still count at t=9.99"
    clock.now = 10.0
    assert limiter.allow() is True, "calls at t=0 no longer count at t=10"


def test_blocked_calls_are_not_counted():
    clock = FakeClock()
    limiter = RateLimiter(1, 10, clock)
    assert limiter.allow() is True
    clock.now = 5
    assert limiter.allow() is False
    clock.now = 10
    assert limiter.allow() is True, "the blocked call at t=5 must not count"


def test_sliding_window():
    clock = FakeClock()
    limiter = RateLimiter(2, 10, clock)
    assert limiter.allow()          # t=0
    clock.now = 6
    assert limiter.allow()          # t=6
    clock.now = 10
    assert limiter.allow()          # t=0 expired, t=6 still counts -> room for one
    assert not limiter.allow()      # now t=6 and t=10 count


def test_reads_the_clock_it_was_given():
    calls = []

    def clock():
        calls.append(1)
        return 0.0

    RateLimiter(1, 5, clock).allow()
    assert calls, "allow() must call the clock function"


@pytest.mark.parametrize("max_calls, per_seconds", [(0, 10), (-1, 10), (1, 0), (1, -5)])
def test_bad_arguments(max_calls, per_seconds):
    with pytest.raises(ValueError):
        RateLimiter(max_calls, per_seconds, lambda: 0.0)
