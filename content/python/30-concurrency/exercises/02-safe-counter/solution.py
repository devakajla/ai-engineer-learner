import threading


class SafeCounter:
    def __init__(self, start=0):
        self._value = start
        self._lock = threading.Lock()

    def increment(self, n=1):
        with self._lock:
            self._value += n

    @property
    def value(self):
        return self._value

    def reset(self):
        with self._lock:
            self._value = 0
