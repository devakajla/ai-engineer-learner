from fastapi.testclient import TestClient

import solution
from solution import app

client = TestClient(app)


def test_periods():
    assert client.get("/reports/daily").json() == {"period": "daily", "days": 1, "offset": 0}
    assert client.get("/reports/weekly").json() == {"period": "weekly", "days": 7, "offset": 0}
    assert client.get("/reports/monthly").json() == {"period": "monthly", "days": 30, "offset": 0}


def test_offset():
    assert client.get("/reports/weekly?offset=2").json() == {"period": "weekly", "days": 7, "offset": 2}
    assert client.get("/reports/weekly?offset=-1").status_code == 422


def test_invalid_period():
    assert client.get("/reports/yearly").status_code == 422


def test_enum_exists():
    assert {p.value for p in solution.Period} == {"daily", "weekly", "monthly"}
