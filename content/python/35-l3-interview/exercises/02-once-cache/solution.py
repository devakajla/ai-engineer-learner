import threading


class OnceCache:
    def __init__(self):
        self._data = {}
        self._lock = threading.Lock()

    def get_or_compute(self, key, compute):
        with self._lock:
            if key not in self._data:
                self._data[key] = compute(key)
            return self._data[key]

    def __len__(self):
        return len(self._data)
