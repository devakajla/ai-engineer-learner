from typing import Annotated

from fastapi import Cookie, FastAPI, Form, HTTPException, Response

app = FastAPI()


@app.post("/login")
def login(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    response: Response,
):
    if username != "dev" or password != "secret123":
        raise HTTPException(status_code=401, detail="Wrong username or password")
    response.set_cookie(key="session", value="abc123", httponly=True)
    return {"ok": True}


@app.get("/me")
def me(session: Annotated[str | None, Cookie()] = None):
    if session != "abc123":
        raise HTTPException(status_code=401, detail="Not logged in")
    return {"user": "dev"}
