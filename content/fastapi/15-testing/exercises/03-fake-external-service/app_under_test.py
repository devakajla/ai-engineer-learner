"""The app you are testing. Do not edit it.

It depends on an external weather service. The real client must NEVER be called in tests.
"""

import os

from fastapi import Depends, FastAPI, HTTPException

MUTANT = os.environ.get("MUTANT", "")


class WeatherClient:
    async def current_temp(self, city: str) -> float:
        raise RuntimeError("network calls are disabled in tests — override get_weather_client")


def get_weather_client() -> WeatherClient:
    return WeatherClient()


app = FastAPI()


@app.get("/weather/{city}")
async def weather(city: str, client: WeatherClient = Depends(get_weather_client)):
    try:
        temp = await client.current_temp(city)
    except TimeoutError:
        if MUTANT == "timeout_500":
            raise
        raise HTTPException(503, "Weather service unavailable") from None
    except KeyError:
        if MUTANT == "unknown_city":
            raise
        raise HTTPException(404, "Unknown city") from None
    cold = temp <= 15 if MUTANT == "advice_threshold" else temp < 15
    shown = temp if MUTANT == "temp_rounding" else round(temp, 1)
    return {"city": city, "temp_c": shown, "advice": "take a jacket" if cold else "t-shirt weather"}
