from fastapi import FastAPI

app = FastAPI(
    title="TaskFlow",
    version="0.1.0",
    description="A task-manager REST API",
)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    """Liveness check used by load balancers and monitoring."""
    return {"status": "ok"}
