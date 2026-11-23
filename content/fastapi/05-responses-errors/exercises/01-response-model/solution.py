from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

USERS = {
    1: {"id": 1, "email": "dev@x.io", "name": "Dev", "password_hash": "$2b$12$abc"},
    2: {"id": 2, "email": "ana@x.io", "name": "Ana", "password_hash": "$2b$12$def"},
}


class UserOut(BaseModel):
    id: int
    email: str
    name: str


@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    user = USERS.get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
