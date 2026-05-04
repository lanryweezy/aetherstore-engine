from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class Product(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    price: float
    brand_id: str
    category: str
    size_chart: dict
    material: str
    colors: List[str]
    dimensions: dict
    asset_urls: dict
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Store(BaseModel):
    id: Optional[str] = None
    name: str
    brand_id: str
    description: str
    template: str
    products: List[str]
    settings: dict
    is_active: bool = True
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str
    user_id: str
