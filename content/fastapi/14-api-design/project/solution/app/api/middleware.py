import logging
import time
import uuid

from fastapi import FastAPI, Request

from app.core.logging import request_id_var

logger = logging.getLogger("taskflow.access")


def register_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        token = request_id_var.set(request_id)
        start = time.perf_counter()
        try:
            response = await call_next(request)
            elapsed_ms = (time.perf_counter() - start) * 1000
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.1f}"
            logger.info("%s %s -> %s (%.1f ms)", request.method, request.url.path, response.status_code, elapsed_ms)
            return response
        finally:
            request_id_var.reset(token)
