"""Maps domain errors to HTTP responses — the only place that knows both."""

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.errors import AppError, ConflictError, NotFoundError

logger = logging.getLogger("taskflow.errors")

STATUS_FOR: dict[type[AppError], int] = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    ConflictError: status.HTTP_409_CONFLICT,
}


async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    code = next((s for cls, s in STATUS_FOR.items() if isinstance(exc, cls)), status.HTTP_400_BAD_REQUEST)
    return JSONResponse(status_code=code, content={"detail": exc.message, "code": exc.code})


async def handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "code": "internal_error"},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, handle_app_error)
    app.add_exception_handler(Exception, handle_unexpected)
