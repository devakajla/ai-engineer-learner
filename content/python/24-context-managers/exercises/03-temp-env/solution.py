import os


class temp_env:
    def __init__(self, **values: str | None) -> None:
        self.values = values
        self._saved: dict[str, str | None] = {}

    def __enter__(self):
        for name, value in self.values.items():
            self._saved[name] = os.environ.get(name)
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
        return self

    def __exit__(self, exc_type, exc, tb):
        for name, old in self._saved.items():
            if old is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = old
        return False
