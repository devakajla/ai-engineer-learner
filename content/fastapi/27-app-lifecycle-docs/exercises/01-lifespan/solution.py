from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

EVENTS: list[str] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    EVENTS.append("start")
    app.state.visits = 0
    yield
    EVENTS.append("stop")


app = FastAPI(lifespan=lifespan)


@app.get("/visit")
def visit(request: Request):
    request.app.state.visits += 1
    return {"visits": request.app.state.visits}


@app.get("/events")
def events():
    return {"events": EVENTS}
