from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

EVENTS: list[str] = []
