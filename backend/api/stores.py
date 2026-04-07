# api/stores.py
# Store management API endpoints for Aetherstore Engine

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_active_user
from models import Store, Brand
from crud import get_store, get_brand, create_store, update_store, delete_store
from .subscriptions import SUBSCRIPTION_PLANS

router = APIRouter()

# Pydantic models for request/response
class StoreCreate(BaseModel):
    brand_id: str
    name: str
    template: Optional[str] = "modern-gallery"
    description: Optional[str] = None
    settings: Optional[dict] = {}
    scene_state: Optional[dict] = {}
    is_published: Optional[bool] = False

class StoreUpdate(BaseModel):
    name: Optional[str] = None
    template: Optional[str] = None
    description: Optional[str] = None
    settings: Optional[dict] = None
    scene_state: Optional[dict] = None
    is_published: Optional[bool] = None
    is_active: Optional[bool] = None

class StoreResponse(BaseModel):
    id: str
    brand_id: str
    name: str
    template: str
    description: Optional[str] = None
    settings: dict
    scene_state: dict
    is_published: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True

@router.post("/", response_model=StoreResponse, status_code=status.HTTP_201_CREATED)
async def create_new_store(store: StoreCreate, current_user = Depends(get_current_active_user), db: Session = Depends(get_db)):
    # Verify brand and ownership
    brand = get_brand(db, store.brand_id)
    if not brand or brand.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to manage this brand")

    # FEATURE GATING: Check store limits
    subscription = brand.settings.get("subscription", {})
    plan_name = subscription.get("plan", "starter")
    plan_limits = SUBSCRIPTION_PLANS.get(plan_name, SUBSCRIPTION_PLANS["starter"])

    current_stores_count = db.query(Store).filter(Store.brand_id == brand.id).count()
    limit = plan_limits["features"]["stores"]

    if limit != "unlimited" and current_stores_count >= limit:
        raise HTTPException(
            status_code=403,
            detail=f"Store limit reached for {plan_name} plan. Upgrade to create more stores."
        )

    store_data = store.dict()
    db_store = create_store(db, store_data)
    return db_store

@router.get("/", response_model=List[StoreResponse])
async def list_stores(brand_id: Optional[str] = None, current_user = Depends(get_current_active_user), db: Session = Depends(get_db)):
    query = db.query(Store)
    if brand_id:
        query = query.filter(Store.brand_id == brand_id)
    return query.all()

@router.get("/{store_id}", response_model=StoreResponse)
async def read_store(store_id: str, db: Session = Depends(get_db)):
    db_store = get_store(db, store_id)
    if not db_store:
        raise HTTPException(status_code=404, detail="Store not found")
    return db_store

@router.put("/{store_id}", response_model=StoreResponse)
async def update_existing_store(store_id: str, store: StoreUpdate, current_user = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_store = get_store(db, store_id)
    if not db_store:
        raise HTTPException(status_code=404, detail="Store not found")

    # Ownership check
    brand = get_brand(db, db_store.brand_id)
    if brand.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    update_data = store.dict(exclude_unset=True)
    return update_store(db, store_id, update_data)

@router.get("/{store_id}/layout", response_model=dict)
async def get_store_layout(store_id: str, db: Session = Depends(get_db)):
    """Retrieve the custom 3D scene state for the store builder"""
    db_store = get_store(db, store_id)
    if not db_store:
        raise HTTPException(status_code=404, detail="Store not found")
    return db_store.scene_state or {}

@router.put("/{store_id}/layout")
async def save_store_layout(store_id: str, layout: dict, current_user = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Persist the 3D position/rotation of all props in the virtual store"""
    db_store = get_store(db, store_id)
    if not db_store:
        raise HTTPException(status_code=404, detail="Store not found")

    brand = get_brand(db, db_store.brand_id)
    if brand.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    db_store.scene_state = layout
    db_store.updated_at = datetime.utcnow()
    db.commit()
    return {"status": "layout saved"}

@router.delete("/{store_id}")
async def delete_existing_store(store_id: str, current_user = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_store = get_store(db, store_id)
    if not db_store:
        raise HTTPException(status_code=404, detail="Store not found")

    brand = get_brand(db, db_store.brand_id)
    if brand.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    delete_store(db, store_id)
    return {"message": "Store deleted"}
