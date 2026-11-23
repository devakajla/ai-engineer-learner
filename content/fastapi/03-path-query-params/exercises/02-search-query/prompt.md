# Search with query parameters

Create `GET /search` with query parameters:

- `q`: **required** string, 2–50 characters
- `limit`: int, default **10**, between **1 and 50**
- `exact`: bool, default **false**

Return them back: `{"q": ..., "limit": ..., "exact": ...}`.

```text
GET /search?q=fastapi             -> {"q": "fastapi", "limit": 10, "exact": false}
GET /search?q=py&limit=5&exact=1  -> {"q": "py", "limit": 5, "exact": true}
GET /search                       -> 422  (q missing)
GET /search?q=a                   -> 422  (too short)
GET /search?q=abc&limit=100       -> 422  (limit too big)
```
