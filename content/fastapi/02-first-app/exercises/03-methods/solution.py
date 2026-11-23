from fastapi import FastAPI

app = FastAPI()


@app.get("/items")
def list_items():
    return []


@app.post("/items")
def create_item():
    return {"created": True}


@app.delete("/items")
def delete_items():
    return {"deleted": 0}
