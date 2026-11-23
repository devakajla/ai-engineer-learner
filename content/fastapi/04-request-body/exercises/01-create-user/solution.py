from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI()


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=50)
    email: str = Field(pattern=r".+@.+")
    age: int = Field(ge=13, le=120)
    bio: str | None = Field(default=None, max_length=200)


@app.post("/users")
def create_user(payload: UserCreate):
    return {"id": 1, **payload.model_dump()}
