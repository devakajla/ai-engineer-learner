# Run code at startup and shutdown

Create `app` with a **lifespan**.

- `EVENTS` is a module-level list (already in the starter).
- At **startup**: append `"start"` to `EVENTS`, and set `app.state.visits = 0`.
- At **shutdown**: append `"stop"` to `EVENTS`.
- `GET /visit` adds 1 to `app.state.visits` and answers `{"visits": <new number>}`.
- `GET /events` answers `{"events": <EVENTS>}`.

The tests use `with TestClient(app) as client:`. The lifespan only runs inside that `with` block.

```text
(start the app)      EVENTS == ["start"]
GET /visit           -> {"visits": 1}
GET /visit           -> {"visits": 2}
(stop the app)       EVENTS == ["start", "stop"]
```

**Think first:** Why is `app.state` a better place for the visit counter than a global variable? (Think of tests and of many apps in one process.)

**Hint:** `from contextlib import asynccontextmanager`, `async def lifespan(app): ...; yield; ...`, and `FastAPI(lifespan=lifespan)`. In a route, reach the app with `request.app.state`.
