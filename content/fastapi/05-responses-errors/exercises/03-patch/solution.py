from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

PROFILE = {"name": "Dev", "bio": "Backend dev", "city": "Pune"}


class ProfileUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    bio: str | None = None
    city: str | None = None


@app.patch("/profile")
def update_profile(payload: ProfileUpdate):
    PROFILE.update(payload.model_dump(exclude_unset=True))
    return PROFILE
