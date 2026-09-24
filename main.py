from fastapi import FastAPI
app= FastAPI()
@app.get("/")
def read_root():
    return {"Message": "Hello, FastAPI!"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id, "message": f"This is your {item_id}th item."}

@app.get("/search/")
def search_items(query: str):
    return {"query":query}