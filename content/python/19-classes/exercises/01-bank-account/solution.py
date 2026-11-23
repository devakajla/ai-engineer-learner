class BankAccount:
    def __init__(self, owner: str, balance: float = 0) -> None:
        if balance < 0:
            raise ValueError("balance cannot be negative")
        self.owner = owner
        self._balance = balance

    @property
    def balance(self) -> float:
        return self._balance

    def deposit(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("amount must be positive")
        self._balance += amount
        return self._balance

    def withdraw(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("amount must be positive")
        if amount > self._balance:
            raise ValueError("insufficient funds")
        self._balance -= amount
        return self._balance

    def __repr__(self) -> str:
        return f"BankAccount(owner={self.owner!r}, balance={self._balance})"
