from types import SimpleNamespace as NS

from solution import collect_stream


def chunk(text):
    return NS(choices=[NS(delta=NS(content=text))])


def test_joins_pieces():
    stream = [chunk("Hel"), chunk("lo"), chunk(" world")]
    assert collect_stream(stream) == "Hello world"


def test_skips_none_and_empty_pieces():
    stream = [chunk(None), chunk("Hel"), chunk(""), chunk("lo"), chunk(None)]
    assert collect_stream(stream) == "Hello"


def test_skips_chunks_without_choices():
    stream = [chunk("a"), NS(choices=[]), chunk("b")]
    assert collect_stream(stream) == "ab", "a chunk with an empty choices list must be skipped"


def test_empty_stream_and_generator():
    assert collect_stream([]) == ""

    def pieces():
        yield chunk("x")
        yield chunk("y")

    assert collect_stream(pieces()) == "xy", "the stream can be any iterable, even a generator"
