from typing import Annotated

from fastapi import FastAPI, Query

app = FastAPI()


@app.get("/search")
def search(
    q: Annotated[str, Query(min_length=2, max_length=50)],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    exact: bool = False,
):
    return {"q": q, "limit": limit, "exact": exact}
