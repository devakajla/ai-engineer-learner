# Async SQLAlchemy CRUD

Build an async items API:

- `engine = create_async_engine("sqlite+aiosqlite://", poolclass=StaticPool)` and `SessionLocal = async_sessionmaker(engine, expire_on_commit=False)`
- model `Item` → `items`: `id`, `name` (`String(100)`), `qty` (int, default 0)
- `async def init_db()` creates the tables (`async with engine.begin() as conn: await conn.run_sync(Base.metadata.create_all)`); call it from the app's **lifespan**
- `async def get_db()` — yields an `AsyncSession`
- schemas `ItemIn(name 1–100, qty ≥ 0)`, `ItemOut(id, name, qty)` with `from_attributes=True`
- **async** routes:
  - `POST /items` → 201 `ItemOut`
  - `GET /items` → list, ordered by id
  - `PATCH /items/{item_id}/qty?delta=<int>` → adds `delta` to `qty`; 404 if missing; 409 `{"detail": "Not enough stock"}` if qty would go below 0

The tests use `with TestClient(app) as client:` so the lifespan runs.
