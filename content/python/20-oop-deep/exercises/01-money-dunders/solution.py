class Money:
    def __init__(self, amount: int, currency: str = "INR") -> None:
        self.amount = amount
        self.currency = currency

    def __repr__(self) -> str:
        return f"Money({self.amount}, {self.currency!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return (self.amount, self.currency) == (other.amount, other.currency)

    def __hash__(self) -> int:
        return hash((self.amount, self.currency))

    def _check(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValueError("currency mismatch")

    def __add__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        self._check(other)
        return Money(self.amount + other.amount, self.currency)

    def __lt__(self, other: "Money") -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        self._check(other)
        return self.amount < other.amount

    def __bool__(self) -> bool:
        return self.amount != 0
