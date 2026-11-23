from types import SimpleNamespace as NS


def chunk(text):
    return NS(choices=[NS(delta=NS(content=text))])

from solution import sse_safe


def broken():
    yield chunk("a")
    raise RuntimeError("boom")


def broken_at_start():
    raise ValueError("no connection")
    yield chunk("never")


def test_error_in_middle():
    out = sse_safe(broken())
    assert out == ["event: token\ndata: a\n\n", "event: error\ndata: stream failed: boom\n\n"]


def test_error_at_start():
    out = sse_safe(broken_at_start())
    assert out == ["event: error\ndata: stream failed: no connection\n\n"]


def test_normal_stream_has_done():
    out = sse_safe([chunk("x"), chunk(None)])
    assert out == ["event: token\ndata: x\n\n", "event: done\ndata: [DONE]\n\n"]


def test_no_done_after_error():
    out = sse_safe(broken())
    assert not any("done" in e for e in out)


def test_custom_event_name():
    assert sse_safe([chunk("x")], event="delta")[0].startswith("event: delta")
