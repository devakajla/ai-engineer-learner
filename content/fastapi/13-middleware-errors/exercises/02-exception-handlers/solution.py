import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppError(Exception):
    code = "app_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    code = "not_found"


class ConflictError(AppError):
    code = "conflict"


USERS = {1: "dev@x.io"}

app = FastAPI()

STATUS_FOR: dict[type[AppError], int] = {NotFoundError: 404, ConflictError: 409}


@app.exception_handler(AppError)
async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    status = next((code for cls, code in STATUS_FOR.items() if isinstance(exc, cls)), 400)
    return JSONResponse(status_code=status, content={"detail": exc.message, "code": exc.code})


@app.exception_handler(Exception)
async def handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error", "code": "internal_error"})


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    if user_id not in USERS:
        raise NotFoundError(f"User {user_id} not found")
    return {"id": user_id, "email": USERS[user_id]}


@app.post("/users", status_code=201)
async def create_user(email: str):
    if email in USERS.values():
        raise ConflictError("Email already registered")
    new_id = max(USERS) + 1
    USERS[new_id] = email
    return {"id": new_id, "email": email}


@app.get("/boom")
async def boom():
    raise RuntimeError("secret db password")
