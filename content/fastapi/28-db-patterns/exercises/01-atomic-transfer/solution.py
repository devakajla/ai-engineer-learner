from sqlalchemy import String, select, update
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class InsufficientFunds(Exception):
    pass


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner: Mapped[str] = mapped_column(String(50))
    balance: Mapped[int] = mapped_column(default=0)


def open_account(session: Session, owner: str, balance: int = 0) -> Account:
    account = Account(owner=owner, balance=balance)
    session.add(account)
    session.commit()
    session.refresh(account)
    return account


def transfer(session: Session, from_id: int, to_id: int, amount: int) -> None:
    if amount <= 0 or from_id == to_id:
        raise ValueError("amount must be above 0 and accounts must differ")
    try:
        if session.get(Account, from_id) is None or session.get(Account, to_id) is None:
            raise LookupError("account not found")
        taken = session.execute(
            update(Account)
            .where(Account.id == from_id, Account.balance >= amount)
            .values(balance=Account.balance - amount)
        )
        if taken.rowcount == 0:
            raise InsufficientFunds(f"account {from_id} has less than {amount}")
        session.execute(
            update(Account).where(Account.id == to_id).values(balance=Account.balance + amount)
        )
        session.commit()
    except Exception:
        session.rollback()
        raise
