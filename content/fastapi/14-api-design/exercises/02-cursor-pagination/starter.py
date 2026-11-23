import base64
import json
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query

app = FastAPI()

EVENTS = [{"id": i, "type": "click"} for i in range(1, 96)]
