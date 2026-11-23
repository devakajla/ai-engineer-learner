from pydantic import BaseModel, Field, field_validator, model_validator


class SignupForm(BaseModel):
    username: str
    email: str
    password: str
    password_confirm: str
    age: int | None = None
