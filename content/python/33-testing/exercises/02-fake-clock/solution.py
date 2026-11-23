from collections import deque


class RateLimiter:
    def __init__(self, max_calls, per_seconds, clock):
        if max_calls < 1:
            raise ValueError("max_calls must be at least 1")
        if per_seconds <= 0:
            raise ValueError("per_seconds must be positive")
        self.max_calls = max_calls
        self.per_seconds = per_seconds
        self.clock = clock
        self._times = deque()

    def allow(self):
        now = self.clock()
        while self._times and self._times[0] <= now - self.per_seconds:
            self._times.popleft()
        if len(self._times) >= self.max_calls:
            return False
        self._times.append(now)
        return True
