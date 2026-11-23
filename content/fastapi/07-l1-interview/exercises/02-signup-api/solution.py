from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI()

USERS: list[dict] = []


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8)
    name: str = Field(min_length=1, max_length=50)


class UserOut(BaseModel):
    id: int
    email: str
    name: str


@app.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate):
    email = payload.email.lower()
    if any(u["email"] == email for u in USERS):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = {
        "id": max((u["id"] for u in USERS), default=0) + 1,
        "email": email,
        "name": payload.name,
        "password": payload.password,
    }
    USERS.append(user)
    return user


@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    for user in USERS:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
