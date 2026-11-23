import pytest

from solution import Stack, last_or_default


def test_stack():
    s = Stack.from_items([1, 2, 3])
    assert (s.pop(), s.peek(), len(s)) == (3, 2, 2)
    assert bool(s) is True


def test_empty():
    s = Stack()
    assert s.peek() is None and len(s) == 0 and not s
    with pytest.raises(IndexError, match="empty"):
        s.pop()


def test_is_generic():
    assert Stack[int] is not None, "Stack must be generic (Stack[int] must work)"
    assert getattr(Stack, "__type_params__", None) or getattr(Stack, "__parameters__", None)


def test_last_or_default():
    assert last_or_default([1, 2], 0) == 2
    assert last_or_default([], "none") == "none"
