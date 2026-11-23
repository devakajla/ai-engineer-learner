import os

from fastapi import FastAPI, HTTPException, UploadFile

app = FastAPI()

MAX_BYTES = 1024
ALLOWED_TYPES = {"image/png", "image/jpeg"}


@app.post("/avatar", status_code=201)
def upload_avatar(file: UploadFile):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Only PNG or JPEG images")
    data = file.file.read(MAX_BYTES + 1)
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File too large")
    name = os.path.basename((file.filename or "").replace("\\", "/"))
    return {"filename": name, "content_type": file.content_type, "size": len(data)}
