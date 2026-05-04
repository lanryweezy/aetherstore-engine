from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import uuid
from database import get_db
from models import ProductDB, StoreDB
from schemas import Product, Store

router = APIRouter(prefix="/commerce", tags=["Commerce-V2"])

@router.get("/products", response_model=List[Product])
async def get_products(db: Session = Depends(get_db)):
    return db.query(ProductDB).all()

@router.post("/products", response_model=Product)
async def create_product(product: Product, db: Session = Depends(get_db)):
    db_product = ProductDB(**product.dict())
    if not db_product.id: db_product.id = str(uuid.uuid4())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/stores", response_model=List[Store])
async def get_stores(db: Session = Depends(get_db)):
    return db.query(StoreDB).all()

@router.post("/stores", response_model=Store)
async def create_store(store: Store, db: Session = Depends(get_db)):
    db_store = StoreDB(**store.dict())
    if not db_store.id: db_store.id = str(uuid.uuid4())
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    return db_store

@router.get("/stores/{store_id}", response_model=Store)
async def get_store(store_id: str, db: Session = Depends(get_db)):
    store = db.query(StoreDB).filter(StoreDB.id == store_id).first()
    if not store: raise HTTPException(status_code=404, detail="Store not found")
    return store
