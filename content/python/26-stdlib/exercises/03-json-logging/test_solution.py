import logging
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from solution import import_rows, to_json


def test_to_json():
    out = to_json({"price": Decimal("9.99"), "at": datetime(2026, 1, 1, tzinfo=UTC), "tags": {"b", "a"}})
    assert out == '{"at": "2026-01-01T00:00:00+00:00", "price": "9.99", "tags": ["a", "b"]}'


def test_to_json_unknown_type():
    with pytest.raises(TypeError):
        to_json({"x": object()})


def test_import_rows_logs(caplog, capsys):
    caplog.set_level(logging.INFO)
    assert import_rows([{"id": 1}, {"name": "x"}, {"id": 3}]) == [1, 3]
    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warnings) == 1 and warnings[0].getMessage() == "skipping row 1: missing id"
    assert any(r.levelno == logging.INFO and r.getMessage() == "imported 2 rows" for r in caplog.records)
    assert capsys.readouterr().out == "", "use logging, not print"
    assert warnings[0].name == "solution", "use logging.getLogger(__name__)"
