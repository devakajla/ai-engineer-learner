from types import SimpleNamespace as NS


def chunk(text):
    return NS(choices=[NS(delta=NS(content=text))])

from solution import sse_events


def test_events():
    out = sse_events([chunk("Hel"), chunk(None), chunk("lo")])
    assert out == [
        "event: token\ndata: Hel\n\n",
        "event: token\ndata: lo\n\n",
        "event: done\ndata: [DONE]\n\n",
    ]


def test_custom_event_name():
    out = sse_events([chunk("x")], event="delta")
    assert out[0] == "event: delta\ndata: x\n\n"


def test_empty_stream():
    assert sse_events([]) == ["event: done\ndata: [DONE]\n\n"]


def test_chunks_without_choices_are_skipped():
    out = sse_events([chunk("a"), NS(choices=[])])
    assert len(out) == 2


def test_multiline_token():
    out = sse_events([chunk("a\nb")])
    assert out[0] == "event: token\ndata: a\ndata: b\n\n"
