import logging
import uuid
from contextvars import ContextVar

from fastapi import FastAPI, Request

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


logger = logging.getLogger("notes")
logger.addFilter(RequestIdFilter())

app = FastAPI()


@app.middleware("http")
async def request_logging(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
    token = request_id_var.set(request_id)
    try:
        response = await call_next(request)
        logger.info("%s %s -> %s", request.method, request.url.path, response.status_code)
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        request_id_var.reset(token)


@app.get("/notes")
async def list_notes():
    logger.info("listing notes")
    return []
