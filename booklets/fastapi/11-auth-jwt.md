# 11. Authentication: register, login and JWT

Right now everyone is "user 1". In this chapter we add real users: sign up, log in, and protect the routes. Read chapter 7 of the Backend booklet first if the ideas (hashing, JWT, 401 vs 403) are new. Here we build them.

## The plan

@@ vflow | Figure 11.1: the login flow we will build.
POST /auth/register|store the user with a hashed password|blue -email + password-> POST /auth/login|check the password, return a signed token|green -token in the Authorization header-> GET /tasks (any route)|get_current_user reads the token and loads the user|yellow
@@ end

The key trick is **dependency injection** from chapter 7. We will change **one** dependency, `get_current_user_id`, into a real `get_current_user`. The routes barely change.

## Steps

::: {.step}
Step 1: install and configure
:::

```bash
uv add pyjwt argon2-cffi python-multipart
```

| Package | Why |
| --- | --- |
| `pyjwt` | create and check JWT tokens |
| `argon2-cffi` | hash passwords with Argon2, a strong, slow hash |
| `python-multipart` | read form data (the login form uses it) |

Add to `Settings`:

```python
secret_key: str = "change-me-to-a-long-random-string-0123456789"
access_token_minutes: int = 15
```

Make a **real** secret and put it in `.env` (never in git):

```bash
openssl rand -hex 32
# -> 9f2c...  (64 hex characters; copy it)
```

```
SECRET_KEY=9f2c...your-long-random-value
```

If the secret leaks, anyone can make valid tokens. Treat it like a password.

::: {.step}
Step 2: security helpers in `core/`
:::

`app/core/security.py`. Password hashing and tokens are used by many parts, so they belong in `core`:

```python
from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.core.config import get_settings

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False


def create_access_token(user_id: int) -> str:
    settings = get_settings()
    expires = datetime.now(UTC) + timedelta(minutes=settings.access_token_minutes)
    payload = {"sub": str(user_id), "exp": expires}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_access_token(token: str) -> int | None:
    """Return the user id, or None if the token is bad or expired."""
    try:
        payload = jwt.decode(token, get_settings().secret_key, algorithms=["HS256"])
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None
```

Points to understand:

- `hash_password` creates a **salted** Argon2 hash. The same password gives a different hash each time. Nobody can reverse it.
- The token payload has `sub` (the user id) and `exp` (expiry). `jwt.decode` checks the **signature and the expiry** for you.
- `algorithms=["HS256"]` is required. Never skip it.
- `decode_access_token` returns `None` on any problem, so the caller has one simple check.

::: {.step}
Step 3: schemas for users and tokens
:::

`app/schemas/user.py`:

```python
from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

`UserCreate` (input, has a password) and `UserOut` (output, has **no** password) are separate on purpose, as chapter 5 taught.

::: {.step}
Step 4: repository, errors and service
:::

Add two errors to `app/core/exceptions.py`:

```python
class EmailTaken(Exception):
    pass


class InvalidCredentials(Exception):
    pass
```

`app/repositories/user_repo.py`:

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        return await self.session.scalar(select(User).where(User.email == email))

    async def add(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
```

`app/services/auth_service.py`:

```python
from app.core.exceptions import EmailTaken, InvalidCredentials
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserCreate


class AuthService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def register(self, data: UserCreate) -> User:
        if await self.repo.get_by_email(data.email):
            raise EmailTaken()
        user = User(email=data.email, password_hash=hash_password(data.password))
        return await self.repo.add(user)

    async def login(self, email: str, password: str) -> str:
        user = await self.repo.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise InvalidCredentials()
        return create_access_token(user.id)
```

Look at `login`: both "no such user" and "wrong password" raise the **same** error. This hides which emails exist, so an attacker learns nothing.

::: {.step}
Step 5: the dependency that finds the current user
:::

In `app/api/deps.py`, **replace** the temporary `get_current_user_id` with the real thing:

```python
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.services.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(UserRepository(session))


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep
) -> User:
    user_id = decode_access_token(token)
    user = await UserRepository(session).get(user_id) if user_id else None
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
CurrentUser = Annotated[User, Depends(get_current_user)]
```

What happens on a request:

1. `OAuth2PasswordBearer` reads the header `Authorization: Bearer <token>` and gives you the token. If the header is missing, it answers `401` itself.
2. We decode the token to a user id, then load that user from the database.
3. If anything is wrong, we raise `401`. Otherwise the route receives a `User` object.

`tokenUrl` tells the `/docs` page where to log in. That makes the **Authorize** button work.

::: {.step}
Step 6: the auth routes
:::

`app/api/routes/auth.py`:

```python
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import AuthServiceDep, CurrentUser
from app.core.exceptions import EmailTaken, InvalidCredentials
from app.schemas.user import Token, UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, service: AuthServiceDep):
    try:
        return await service.register(data)
    except EmailTaken:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")


@router.post("/login", response_model=Token)
async def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], service: AuthServiceDep):
    try:
        token = await service.login(form.username, form.password)
    except InvalidCredentials:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong email or password")
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
async def me(user: CurrentUser):
    return user
```

The login route reads a **form** (`username` and `password` fields), not JSON. That is the OAuth2 standard, and it is what lets `/docs` log in. We put the email in the `username` field.

Add it to `app/api/router.py`:

```python
from app.api.routes import auth, tasks

api_router.include_router(auth.router)
api_router.include_router(tasks.router)
```

::: {.step}
Step 7: protect the task routes
:::

In `app/api/routes/tasks.py` replace `CurrentUserId` with `CurrentUser`, and use `user.id`:

```python
from app.api.deps import CurrentUser, PaginationDep, TaskServiceDep

@router.get("", response_model=list[TaskOut])
async def list_tasks(user: CurrentUser, service: TaskServiceDep, page: PaginationDep, done: bool | None = None):
    return await service.list_tasks(user.id, done, page.limit, page.offset)

@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(data: TaskCreate, user: CurrentUser, service: TaskServiceDep):
    return await service.create_task(user.id, data)

@router.get("/{task_id}", response_model=TaskOut)
async def get_task(task_id: int, user: CurrentUser, service: TaskServiceDep):
    return await service.get_task(user.id, task_id)

# update_task and delete_task: the same change (owner_id -> user: CurrentUser, user.id)
```

That is the whole change to the routes. The **service did not change at all**. That is the layers and dependency injection paying off.

Because the old data (tasks of "user 1") has no real user, delete the old database and start fresh:

```bash
rm taskflow.db
uv run alembic upgrade head
```

::: {.step}
Step 8: try it
:::

```bash
# 1. sign up
curl -X POST localhost:8000/api/v1/auth/register -H "Content-Type: application/json" \
  -d '{"email": "asha@example.com", "password": "secret123"}'
# -> {"id":1,"email":"asha@example.com"}

# 2. log in (note: form data, with -d and no JSON header)
curl -X POST localhost:8000/api/v1/auth/login -d "username=asha@example.com&password=secret123"
# -> {"access_token":"eyJhbGciOiJIUzI1NiIs...","token_type":"bearer"}

# 3. call a protected route with the token
TOKEN=eyJhbGciOi...            # paste your token
curl localhost:8000/api/v1/tasks -H "Authorization: Bearer $TOKEN"
# -> []

# 4. without a token
curl -i localhost:8000/api/v1/tasks
# -> HTTP/1.1 401 Unauthorized   {"detail":"Not authenticated"}
```

Also open `/docs`: a green **Authorize** button appears. Log in once there, and every "Try it out" sends your token.

## Ownership: the second half of security

Login only proves **who you are**. The next question is **what is yours**. Our service already does it: `get_task` raises `TaskNotFound` when `task.owner_id != owner_id`. Test it. Register a second user, `ravi@example.com`, and ask for Asha's task `1`:

```bash
curl -i localhost:8000/api/v1/tasks/1 -H "Authorization: Bearer $RAVI_TOKEN"
# -> HTTP/1.1 404 Not Found   {"error":"not_found","message":"Task 1 not found"}
```

Ravi gets `404`, not Asha's data. Forgetting this check is the most common serious API bug (IDOR).

## Roles (RBAC) in one dependency

To allow only admins, add a `role` column to `User` (with a migration), then a small dependency **factory**:

```python
def require_role(role: str):
    def checker(user: CurrentUser) -> User:
        if user.role != role:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Not allowed")
        return user
    return checker

@router.delete("/users/{user_id}", dependencies=[Depends(require_role("admin"))])
async def delete_user(user_id: int): ...
```

`require_role("admin")` returns a new checking function. This pattern (a function that returns a function) is a closure. The Python booklet explains it.

## Refresh tokens (the idea)

A 15 minute access token is safe, but nobody wants to log in every 15 minutes. So login also returns a **refresh token** that lives for days. It is stored (hashed) in the database, so you can revoke it. The client sends it to `POST /auth/refresh` to get a new access token. Logging out deletes the refresh token. Try building it as an exercise.

::: {.box .checkpoint}
**Folder now**

```
app/
├── core/          config.py, exceptions.py, security.py (NEW), logging.py
├── models/        user.py, task.py
├── schemas/       task.py, user.py (NEW)
├── repositories/  task_repo.py, user_repo.py (NEW)
├── services/      task_service.py, auth_service.py (NEW)
└── api/
    ├── deps.py                  # get_current_user, CurrentUser, AuthServiceDep
    └── routes/    health.py, tasks.py, auth.py (NEW)
```

**Checkpoint:** register, log in, list tasks with the token (`[]`), then without a token (`401`). A second user cannot read the first user's task (`404`).
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Storing plain or fast-hashed passwords.
- A short or guessable `SECRET_KEY`, or one committed to git.
- A token that never expires.
- Telling the client "email not found" for login. Use one message.
- Logging in with JSON when you used `OAuth2PasswordRequestForm`. It expects a form.
- Checking login but not ownership (IDOR).
- Forgetting `algorithms=[...]` in `jwt.decode`.
- Returning `password_hash` by using the wrong response model.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: How does JWT auth work in FastAPI?**
Login checks the password and returns a signed token. For protected routes, `OAuth2PasswordBearer` reads the `Authorization` header, a dependency decodes and checks the token, loads the user and passes it to the route.

**Q: Why use a dependency for the current user?**
Any route can add `user: CurrentUser` to become protected. It is reusable and testable (you can override it).

**Q: How do you store passwords?**
With a slow, salted hash such as Argon2 or bcrypt.

**Q: How do you restrict a route to admins?**
A dependency that checks `user.role` and raises `403`.

**Q: How do you log a user out with JWT?**
You cannot cancel a signed access token, so keep it short-lived and revoke the refresh token.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Make a `PATCH /api/v1/auth/me` route that lets a user change their email. Which errors can happen?
2. Write a test (by hand with curl) that proves a user cannot delete another user's task.
3. Change the token lifetime to 1 minute, log in, wait 2 minutes and call a protected route. What do you get?
4. Add a `role` column with a default of `"user"` using a migration, and the `require_role` dependency.
5. Design the refresh-token flow: which table, which endpoints, what do you store?
6. **Think:** why do we return the same error for "no such user" and "wrong password"?
:::
