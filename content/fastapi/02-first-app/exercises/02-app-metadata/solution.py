from fastapi import FastAPI

app = FastAPI(title="TaskFlow", version="0.1.0", description="Manage your tasks")


@app.get("/about")
def about():
    return {"name": app.title, "version": app.version}
