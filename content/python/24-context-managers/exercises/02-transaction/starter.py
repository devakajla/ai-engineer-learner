from contextlib import contextmanager


class FakeConnection:
    def __init__(self) -> None:
        self.log: list[str] = []

    def begin(self) -> None:
        self.log.append("begin")

    def execute(self, sql: str) -> None:
        self.log.append(f"execute {sql}")

    def commit(self) -> None:
        self.log.append("commit")

    def rollback(self) -> None:
        self.log.append("rollback")


@contextmanager
def transaction(conn):
    yield conn
