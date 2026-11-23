from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


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
