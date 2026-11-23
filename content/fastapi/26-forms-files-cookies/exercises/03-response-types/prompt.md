# Not every answer is JSON

Create `app` with these routes:

| Route | Answer |
|---|---|
| `GET /page` | an **HTML** page: `<h1>Hello</h1>` (content type `text/html`) |
| `GET /old` | a **redirect** to `/new` with status **301** |
| `GET /new` | plain **text** `new` (content type `text/plain`) |
| `GET /download` | the file `report.txt` (it is next to your code) as a **download**: header `Content-Disposition` must say `attachment` and the file name `report.txt` |
| `GET /profile` | JSON from a `response_model`, but **fields that are `None` are left out** |

For `/profile`, return this dict and use a model `Profile` with `id: int`, `name: str`, `bio: str | None = None`:

```python
{"id": 1, "name": "Ana", "bio": None}      # -> {"id": 1, "name": "Ana"}   (bio is not sent)
```

**Think first:** Why do you need `response_class=HTMLResponse` for the page, when returning a string gives JSON by default?

**Hint:** `HTMLResponse`, `RedirectResponse`, `PlainTextResponse`, `FileResponse` from `fastapi.responses`. `FileResponse(path, filename="report.txt")` sets the download header. Find the file with `Path(__file__).parent / "report.txt"`. For `/profile` look at `response_model_exclude_none=True`.
