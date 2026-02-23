# api/stores.py
# Store management API endpoints for Aetherstore Engine

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

router = APIRouter()

# Pydantic models for request/response
class StoreCreate(BaseModel):
    brand_id: str
    name: str
    template: Optional[str] = "modern-gallery"
    description: Optional[str] = None
    settings: Optional[dict] = {}
    is_published: Optional[bool] = False

class StoreUpdate(BaseModel):
    name: Optional[str] = None
    template: Optional[str] = None
    description: Optional[str] = None
    settings: Optional[dict] = None
    is_published: Optional[bool] = None
    is_active: Optional[bool] = None

class StoreResponse(BaseModel):
    id: str
    brand_id: str
    name: str
    template: str
    description: Optional[str] = None
    settings: dict
    is_published: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True