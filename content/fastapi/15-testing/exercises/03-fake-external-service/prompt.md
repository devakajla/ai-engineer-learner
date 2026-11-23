# Fake an external service

`GET /weather/{city}` (in `app_under_test.py`) calls an external weather API through the dependency `get_weather_client`. The real client refuses to run in tests.

Write a **fake client** class with an async `current_temp(city)` that you can configure to return a temperature or raise an error, and tests that override `get_weather_client` with it. Rules to test:

- returns `{"city", "temp_c", "advice"}` with `temp_c` rounded to **1 decimal**
- `advice` is `"take a jacket"` when temp **< 15**, else `"t-shirt weather"` (15 itself → t-shirt)
- the client raises `TimeoutError` → **503** `{"detail": "Weather service unavailable"}`
- the client raises `KeyError` (unknown city) → **404** `{"detail": "Unknown city"}`
- your fake should record the cities it was asked for — assert the right city was passed

Your suite must pass on the correct app and catch 4 broken versions. Use `TestClient(app, raise_server_exceptions=False)` so unexpected errors become 500 responses instead of crashing the test.
