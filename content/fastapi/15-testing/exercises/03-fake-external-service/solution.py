import pytest
from fastapi.testclient import TestClient

from app_under_test import app, get_weather_client


class FakeWeather:
    def __init__(self, temp: float = 20.0, error: Exception | None = None) -> None:
        self.temp, self.error, self.cities = temp, error, []

    async def current_temp(self, city: str) -> float:
        self.cities.append(city)
        if self.error is not None:
            raise self.error
        return self.temp


@pytest.fixture
def use_fake():
    def install(fake: FakeWeather) -> TestClient:
        app.dependency_overrides[get_weather_client] = lambda: fake
        return TestClient(app, raise_server_exceptions=False)

    yield install
    app.dependency_overrides.clear()


def test_happy_path_and_city_passed(use_fake):
    fake = FakeWeather(temp=21.04)
    r = use_fake(fake).get("/weather/Pune")
    assert r.json() == {"city": "Pune", "temp_c": 21.0, "advice": "t-shirt weather"}
    assert fake.cities == ["Pune"]


@pytest.mark.parametrize(("temp", "advice"), [(14.9, "take a jacket"), (15, "t-shirt weather"), (-3, "take a jacket")])
def test_advice_threshold(use_fake, temp, advice):
    assert use_fake(FakeWeather(temp=temp)).get("/weather/x").json()["advice"] == advice


def test_rounding(use_fake):
    assert use_fake(FakeWeather(temp=18.456)).get("/weather/x").json()["temp_c"] == 18.5


def test_timeout_is_503(use_fake):
    r = use_fake(FakeWeather(error=TimeoutError())).get("/weather/x")
    assert r.status_code == 503 and r.json() == {"detail": "Weather service unavailable"}


def test_unknown_city_404(use_fake):
    r = use_fake(FakeWeather(error=KeyError("atlantis"))).get("/weather/atlantis")
    assert r.status_code == 404 and r.json() == {"detail": "Unknown city"}
