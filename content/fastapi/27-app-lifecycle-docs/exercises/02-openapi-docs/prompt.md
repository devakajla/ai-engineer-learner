# Make the API docs useful

FastAPI builds the docs page from your code. Shape it. Create `app` like this:

- `FastAPI(title="Shop API", version="2.1.0", description="Small shop backend", docs_url="/documentation")`
- a tag description: `openapi_tags=[{"name": "items", "description": "Item operations"}]`

Routes:

| Route | Rules |
|---|---|
| `GET /items` | tag `items`, `summary="List items"`, `operation_id="list_items"`, answers `[{"id": 1}]` |
| `GET /items/old` | tag `items`, `deprecated=True`, answers `[{"id": 1}]` |
| `GET /internal` | hidden from the docs (`include_in_schema=False`) but it **works**: answers `{"secret": true}` |

Check your work with `app.openapi()`, which gives the schema as a dict. The Swagger page must be at `/documentation`, and `/docs` must not exist.

**Think first:** Who reads `/openapi.json`? (Think of tools that make client code.)

**Hint:** Options go on the decorator: `@app.get("/items", tags=[...], summary=..., operation_id=...)`. Put the fixed route `/items/old` anywhere, there is no `{id}` route to clash with.
