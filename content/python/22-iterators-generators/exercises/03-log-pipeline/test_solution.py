import inspect
import types

from solution import filter_level, first_errors, messages, parse

LINES = ["t1 INFO started", "t2 ERROR db down", "", "t3 ERROR retry failed: timeout", "t4 WARN slow"]


def test_parse():
    recs = list(parse(LINES))
    assert recs[1] == {"ts": "t2", "level": "ERROR", "msg": "db down"}
    assert len(recs) == 4, "skip blank lines"
    assert recs[2]["msg"] == "retry failed: timeout"


def test_stages_are_lazy():
    for stage in (parse(LINES), filter_level(iter([]), "ERROR"), messages(iter([]))):
        assert isinstance(stage, types.GeneratorType), "each stage must be a generator"


def test_first_errors():
    assert first_errors(LINES, 1) == ["db down"]
    assert first_errors(LINES, 5) == ["db down", "retry failed: timeout"]


def test_stops_early():
    def source():
        yield "t1 ERROR one"
        yield "t2 ERROR two"
        raise AssertionError("read too far: the pipeline must stop after n errors")

    assert first_errors(source(), 2) == ["one", "two"]
