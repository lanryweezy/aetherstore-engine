from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime
from pydantic import BaseModel

# Database imports (Assuming they are in main.py for now, we'll need to move them later to a database.py)
# For the sake of modularity, I'll assume they will be importable.

router = APIRouter(prefix="/api", tags=["Commerce & Stores"])

# We'll use the SessionLocal and ProductDB/StoreDB from main.py for now
# This is part of the refactor - moving DB setup to its own file.

@router.get("/products")
async def get_products(db: Session = Depends(get_db)):
    return db.query(ProductDB).all()

@router.post("/products")
async def create_product(product: Product, db: Session = Depends(get_db)):
    db_product = ProductDB(**product.dict())
    if not db_product.id: db_product.id = str(uuid.uuid4())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/stores")
async def get_stores(db: Session = Depends(get_db)):
    return db.query(StoreDB).all()

@router.post("/stores")
async def create_store(store: Store, db: Session = Depends(get_db)):
    db_store = StoreDB(**store.dict())
    if not db_store.id: db_store.id = str(uuid.uuid4())
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    return db_store
