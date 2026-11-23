import base64
import binascii
import json
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query

app = FastAPI()

EVENTS = [{"id": i, "type": "click"} for i in range(1, 96)]


def encode_cursor(last_id: int) -> str:
    return base64.urlsafe_b64encode(json.dumps({"id": last_id}).encode()).decode()


def decode_cursor(cursor: str) -> int:
    try:
        data = json.loads(base64.urlsafe_b64decode(cursor.encode()))
        return int(data["id"])
    except (binascii.Error, ValueError, KeyError, TypeError, UnicodeDecodeError):
        raise HTTPException(status_code=400, detail="Invalid cursor") from None


@app.get("/events")
def list_events(limit: Annotated[int, Query(ge=1, le=50)] = 20, cursor: str | None = None):
    items = sorted(EVENTS, key=lambda e: e["id"], reverse=True)
    if cursor is not None:
        last_id = decode_cursor(cursor)
        items = [e for e in items if e["id"] < last_id]
    page = items[:limit]
    has_more = len(items) > limit
    return {"items": page, "next_cursor": encode_cursor(page[-1]["id"]) if has_more and page else None}
