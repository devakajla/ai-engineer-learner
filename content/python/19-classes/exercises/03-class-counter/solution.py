class Ticket:
    _counter = 0

    def __init__(self, title: str) -> None:
        Ticket._counter += 1
        self.id = Ticket._counter
        self.title = title
        self.comments: list[str] = []

    def add_comment(self, text: str) -> None:
        self.comments.append(text)

    @classmethod
    def total_created(cls) -> int:
        return cls._counter

    @classmethod
    def reset_counter(cls) -> None:
        cls._counter = 0
