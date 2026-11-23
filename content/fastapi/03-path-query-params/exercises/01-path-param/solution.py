from typing import Annotated

from fastapi import FastAPI, Path

app = FastAPI()


@app.get("/users/me")
def read_me():
    return {"user_id": "me"}


@app.get("/users/{user_id}")
def read_user(user_id: Annotated[int, Path(ge=1)]):
    return {"user_id": user_id}
