from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, FastAPI, Query

app = FastAPI()

ITEMS = [f"item-{i}" for i in range(50)]
USERS = [f"user-{i}" for i in range(30)]
