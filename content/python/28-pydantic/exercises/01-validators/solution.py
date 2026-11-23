import re

from pydantic import BaseModel, Field, field_validator, model_validator


class SignupForm(BaseModel):
    username: str = Field(min_length=3, max_length=20, pattern=r"^\w+$")
    email: str
    password: str = Field(min_length=8)
    password_confirm: str
    age: int | None = Field(default=None, ge=13)

    @field_validator("username")
    @classmethod
    def lower_username(cls, v: str) -> str:
        return v.lower()

    @field_validator("email")
    @classmethod
    def check_email(cls, v: str) -> str:
        v = v.strip().lower()
        if v.count("@") != 1 or "." not in v.split("@")[1]:
            raise ValueError("invalid email")
        return v

    @field_validator("password")
    @classmethod
    def strong_password(cls, v: str) -> str:
        if not re.search(r"\d", v) or not re.search(r"[A-Z]", v):
            raise ValueError("password needs a digit and an uppercase letter")
        return v

    @model_validator(mode="after")
    def passwords_match(self) -> "SignupForm":
        if self.password != self.password_confirm:
            raise ValueError("passwords do not match")
        return self
