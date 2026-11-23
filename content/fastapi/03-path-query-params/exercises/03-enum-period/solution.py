from enum import Enum
from typing import Annotated

from fastapi import FastAPI, Query

app = FastAPI()


class Period(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


DAYS = {Period.daily: 1, Period.weekly: 7, Period.monthly: 30}


@app.get("/reports/{period}")
def report(period: Period, offset: Annotated[int, Query(ge=0)] = 0):
    return {"period": period.value, "days": DAYS[period], "offset": offset}
