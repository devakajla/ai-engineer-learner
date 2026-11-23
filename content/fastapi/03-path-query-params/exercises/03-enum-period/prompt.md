# Report periods with an Enum

Create an `Enum` called `Period` with values `daily`, `weekly`, `monthly`, and a route `GET /reports/{period}` that returns how many days the period covers:

```text
GET /reports/daily    -> {"period": "daily", "days": 1}
GET /reports/weekly   -> {"period": "weekly", "days": 7}
GET /reports/monthly  -> {"period": "monthly", "days": 30}
GET /reports/yearly   -> 422
```

Also add an optional query parameter `offset` (int, default 0, must be ≥ 0) that is returned too: `GET /reports/weekly?offset=2` → `{"period": "weekly", "days": 7, "offset": 2}`. (When there is no `offset` in the URL, still return `"offset": 0`.)
