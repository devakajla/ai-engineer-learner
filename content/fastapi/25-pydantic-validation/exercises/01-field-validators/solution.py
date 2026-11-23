from fastapi import FastAPI
from pydantic import BaseModel, field_validator

app = FastAPI()


class SignupIn(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def clean_username(cls, value: str) -> str:
        value = value.strip().lower()
        if not 3 <= len(value) <= 20:
            raise ValueError("username must be 3 to 20 characters")
        if not all(ch.isalnum() or ch == "_" for ch in value):
            raise ValueError("username may only have letters, digits and _")
        return value

    @field_validator("password")
    @classmethod
    def strong_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("password must be at least 8 characters")
        if not any(ch.isalpha() for ch in value) or not any(ch.isdigit() for ch in value):
            raise ValueError("password needs a letter and a digit")
        return value


@app.post("/signup", status_code=201)
def signup(payload: SignupIn):
    return {"username": payload.username}
