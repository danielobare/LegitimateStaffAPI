from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- Database setup ---
DATABASE_URL = "mysql+mysqlconnector://root:password@localhost/fastapi_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# --- SQLAlchemy model ---
class ItemModel(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    in_stock = Column(Boolean, default=True)

# Create tables
Base.metadata.create_all(bind=engine)

# --- Pydantic model ---
class Item(BaseModel):
    name: str
    price: float
    in_stock: bool = True

app = FastAPI()

# --- POST endpoint ---
@app.post("/items/", response_model=Item)
def create_item(item: Item):
    db = SessionLocal()
    db_item = ItemModel(name=item.name, price=item.price, in_stock=item.in_stock)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    db.close()
    return item

# --- GET all items ---
@app.get("/items/")
def get_items():
    db = SessionLocal()
    items = db.query(ItemModel).all()
    db.close()
    return items

# --- GET single item ---
@app.get("/items/{item_id}")
def read_item(item_id: int):
    db = SessionLocal()
    item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    db.close()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
