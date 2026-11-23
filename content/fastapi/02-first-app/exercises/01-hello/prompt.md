# Hello, TaskFlow

Create a FastAPI app in a variable named `app` with one route:

- `GET /` → returns `{"message": "Hello, TaskFlow"}`

```python
# expected
GET /  ->  200  {"message": "Hello, TaskFlow"}
```

The tests import `app` from your code and call it with `TestClient`.
