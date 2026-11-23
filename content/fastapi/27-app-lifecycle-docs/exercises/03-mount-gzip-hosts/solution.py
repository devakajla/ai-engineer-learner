from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["testserver", "api.example.com"])

admin = FastAPI()


@admin.get("/stats")
def stats():
    return {"admin": True}


app.mount("/admin", admin)


@app.get("/small")
def small():
    return {"ok": True}


@app.get("/big")
def big():
    return {"data": "x" * 2000}
