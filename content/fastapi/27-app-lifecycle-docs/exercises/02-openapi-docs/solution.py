from fastapi import FastAPI

app = FastAPI(
    title="Shop API",
    version="2.1.0",
    description="Small shop backend",
    docs_url="/documentation",
    openapi_tags=[{"name": "items", "description": "Item operations"}],
)


@app.get("/items", tags=["items"], summary="List items", operation_id="list_items")
def list_items():
    return [{"id": 1}]


@app.get("/items/old", tags=["items"], deprecated=True)
def list_items_old():
    return [{"id": 1}]


@app.get("/internal", include_in_schema=False)
def internal():
    return {"secret": True}
