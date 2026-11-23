class Countdown:
    def __init__(self, start: int) -> None:
        self.current = start

    def __iter__(self):
        return self

    def __next__(self) -> int:
        if self.current <= 0:
            raise StopIteration
        self.current -= 1
        return self.current + 1


def countdown(start: int):
    while start > 0:
        yield start
        start -= 1
