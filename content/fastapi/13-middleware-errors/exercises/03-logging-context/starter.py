import logging
import uuid
from contextvars import ContextVar

from fastapi import FastAPI, Request

app = FastAPI()
