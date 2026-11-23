import pytest

from solution import FakeConnection, transaction


def test_commit():
    conn = FakeConnection()
    with transaction(conn) as c:
        assert c is conn
        c.execute("INSERT x")
    assert conn.log == ["begin", "execute INSERT x", "commit"]


def test_rollback_and_reraise():
    conn = FakeConnection()
    with pytest.raises(RuntimeError):
        with transaction(conn) as c:
            c.execute("INSERT y")
            raise RuntimeError("boom")
    assert conn.log == ["begin", "execute INSERT y", "rollback"]
