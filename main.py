from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

#Defining a request body model
class Item(BaseModel):
    name: str
    role: str
    work_office: str
    salary: float
    active_employee: bool = True #Defaulting to True should no value be provided!
    fraud_system_access: bool = False

#Adding GET endpoint 1
@app.get("/")
def read_root():
    return {"message": "Daniel you are already building APISs!"}

#Adding GET endpoint 2
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "query": q}

#Adding POST endpoint
@app.post("/items/")
def create_item(item: Item):
    return {
        "message": "Daniel you have used POST successfully on this API!",
        "item": item
    }