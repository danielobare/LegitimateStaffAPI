from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
#adding security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional

DATABASE_URL = "mysql+mysqlconnector://root:root@localhost/fastapi_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# SQLAlchemy Model
class ItemModel(Base):
    __tablename__ = "items"
    # id = Column(Integer, primary_key=True, index=True)
    # id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    CALLING_MSISDN = Column(Float, primary_key=True, nullable=False)
    STAFF_NAME = Column(String(100), nullable=False)
    CHANNELS = Column(String(100), nullable=False)
    DATABASE2 = Column(String(100), default="")
    LOGS2 = Column(String (16000), default="")

# Creating them tables
Base.metadata.create_all(bind=engine)

#authsetup
SECRET_KEY = "supersecretkey123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


fake_users_db = {
    "daniel": {
        "username": "daniel",
        "hashed_password": pwd_context.hash("taskHass!"),
    }
}

# Pydantic Model
class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str

class Item(BaseModel):
    CALLING_MSISDN: float
    STAFF_NAME: str
    CHANNELS: str
    DATABASE2: str
    LOGS2: str


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = fake_users_db.get(username)
    if user is None:
        raise credentials_exception
    return user

app = FastAPI()

#Auth route
@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

#CRUD routes with authentication
@app.post("/items/", response_model=Item)
def create_item(item: Item, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    db_item = ItemModel(CALLING_MSISDN=item.CALLING_MSISDN, STAFF_NAME=item.STAFF_NAME, CHANNELS=item.CHANNELS, DATABASE2=item.DATABASE2, LOGS2=item.LOGS2)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    db.close()
    return item

# GET root items
@app.get("/")
def get_root(current_user: User = Depends(get_current_user)):
    return {"message": "This is your root homepage!"}

# GET all items
@app.get("/items/")
def get_items(current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    items = db.query(ItemModel).all()
    db.close()
    return items

# GET a single item
@app.get("/items/{calling_msisdn}")
def read_item(calling_msisdn: float, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    item = db.query(ItemModel).filter(ItemModel.CALLING_MSISDN == calling_msisdn).first()
    db.close()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
