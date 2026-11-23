import os

from fastapi import FastAPI, HTTPException, UploadFile

app = FastAPI()

MAX_BYTES = 1024
ALLOWED_TYPES = {"image/png", "image/jpeg"}
