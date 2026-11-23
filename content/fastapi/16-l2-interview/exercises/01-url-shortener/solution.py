import string

from fastapi import FastAPI, HTTPException, Response, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase

app = FastAPI()

_by_code: dict[str, dict] = {}
_code_by_url: dict[str, str] = {}
_next_id = 1


def encode_base62(n: int) -> str:
    if n == 0:
        return ALPHABET[0]
    digits = []
    while n:
        n, rem = divmod(n, 62)
        digits.append(ALPHABET[rem])
    return "".join(reversed(digits))


class LinkIn(BaseModel):
    url: str = Field(pattern=r"^https?://\S+$", max_length=2048)


def _get(code: str) -> dict:
    link = _by_code.get(code)
    if link is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")
    return link


@app.post("/links", status_code=status.HTTP_201_CREATED)
def shorten(payload: LinkIn, response: Response):
    global _next_id
    existing = _code_by_url.get(payload.url)
    if existing is not None:
        response.status_code = status.HTTP_200_OK
        return {"code": existing, "url": payload.url}
    code = encode_base62(_next_id)
    _next_id += 1
    _by_code[code] = {"code": code, "url": payload.url, "hits": 0}
    _code_by_url[payload.url] = code
    return {"code": code, "url": payload.url}


@app.get("/links/{code}/stats")
def stats(code: str):
    return _get(code)


@app.get("/{code}")
def follow(code: str):
    link = _get(code)
    link["hits"] += 1
    return RedirectResponse(link["url"], status_code=status.HTTP_307_TEMPORARY_REDIRECT)
