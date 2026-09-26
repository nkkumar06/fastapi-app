from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from typing import Optional

app = FastAPI()

DB_URL = "sqlite:///./items.db"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ItemDB(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    age = Column(Integer, nullable=False)
    city = Column(String, nullable=False)
    is_human = Column(Boolean, default=True)
    description = Column(String, nullable=True)


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    age: int = Field(..., ge=0, le=120)
    city: str = Field(..., min_length=1, max_length=50)
    is_human: Optional[bool] = True
    description: Optional[str] = Field(None, max_length=200)

    @validator("name")
    def no_special_characters(cls, value):
        if not value.isalpha():
            raise ValueError("Name must contain only alphabetic characters")
        return value


Base.metadata.create_all(bind=engine)


def item_to_dict(item: ItemDB):
    return {
        "id": item.id,
        "name": item.name,
        "age": item.age,
        "city": item.city,
        "is_human": item.is_human,
        "description": item.description,
    }


@app.get("/")
def read_root():
    return {"Message": "Hello, FastAPI!"}


@app.get("/items")
def read_items():
    db = SessionLocal()
    items = db.query(ItemDB).all()
    db.close()
    return {"items": [item_to_dict(item) for item in items]}


@app.get("/items/{item_id}")
def read_item(item_id: int):
    db = SessionLocal()
    item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    db.close()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id, "item": item_to_dict(item)}


@app.get("/search/{item_id}")
def search_items(item_id: int):
    db = SessionLocal()
    item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    db.close()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item": item_to_dict(item)}


@app.post("/items/")
def post_item(item: ItemCreate):
    db = SessionLocal()
    db_item = ItemDB(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    db.close()
    return {"message": "Item created", "item": item_to_dict(db_item)}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: ItemCreate):
    db = SessionLocal()
    db_item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if db_item is None:
        db.close()
        raise HTTPException(status_code=404, detail="Item not found")

    for key, value in item.dict().items():
        setattr(db_item, key, value)

    db.commit()
    db.refresh(db_item)
    db.close()
    return {"message": "Item updated", "item": item_to_dict(db_item)}


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    db = SessionLocal()
    db_item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if db_item is None:
        db.close()
        raise HTTPException(status_code=404, detail="Item not found")

    deleted_item = item_to_dict(db_item)
    db.delete(db_item)
    db.commit()
    db.close()
    return {"message": "Item deleted", "item": deleted_item}
