# Parse a request line

The first line of an HTTP request looks like `GET /tasks?done=true&limit=5 HTTP/1.1`.

Write `parse_request_line(line)` that returns a dict with:

- `"method"`: the method, e.g. `"GET"`
- `"path"`: the path **without** the query string, e.g. `"/tasks"`
- `"query"`: a dict of query parameters (all values are strings); `{}` if there is none
- `"version"`: e.g. `"HTTP/1.1"`

```python
parse_request_line("GET /tasks?done=true&limit=5 HTTP/1.1")
# -> {"method": "GET", "path": "/tasks", "query": {"done": "true", "limit": "5"}, "version": "HTTP/1.1"}

parse_request_line("DELETE /tasks/7 HTTP/1.1")
# -> {"method": "DELETE", "path": "/tasks/7", "query": {}, "version": "HTTP/1.1"}
```

Keep it simple: you may assume no repeated keys and no URL-encoding. Hint: `split` and `partition` are enough.
