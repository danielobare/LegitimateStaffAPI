from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+mysqlconnector://root:root@localhost/fastapi_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# SQLAlchemy Model
class ItemModel(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    CALLING_MSISDN = Column(Float, nullable=False)
    STAFF_NAME = Column(String(100), nullable=False)
    CHANNELS = Column(String(100), nullable=False)
    DATABASE2 = Column(String(100), default=True)
    LOGS2 = Column(String(16000), default=True)

# Creating them tables
Base.metadata.create_all(bind=engine)

# Pydantic Model
class Item(BaseModel):
    CALLING_MSISDN: float
    STAFF_NAME: str
    CHANNELS: str
    DATABASE2: str
    LOGS2: str

app = FastAPI()

#POST ENDPOINT
@app.post("/items/", response_model=Item)
def create_item(item: Item):
    db = SessionLocal()
    db_item = ItemModel(CALLING_MSISDN=item.CALLING_MSISDN, STAFF_NAME=item.STAFF_NAME, CHANNELS=item.CHANNELS, DATABASE2=item.DATABASE2, LOGS2=item.LOGS2)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    db.close()
    return item

# GET root items
@app.get("/")
def get_root():
    return {"message": "This is your root homepage!"}

# GET all items
@app.get("items/")
def get_items():
    db = SessionLocal()
    items = db.query(ItemModel).all()
    db.close()
    return items

# GET a single item
@app.get("/items/{item_id}")
def read_item(item_id: int):
    db = SessionLocal()
    item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    db.close()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item