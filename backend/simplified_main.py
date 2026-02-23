from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
from pydantic import BaseModel
from typing import Optional, List
import os
from datetime import datetime
import uuid
import asyncio
import logging

# Simplified version without AI dependencies
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Aetherstore Engine API",
    description="The ultimate 3D fashion platform API (Simplified)",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# Pydantic models
class Product(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    price: float
    brand_id: str
    category: str
    size_chart: Optional[dict] = None
    colors: Optional[List[str]] = None
    dimensions: Optional[dict] = None
    asset_urls: Optional[dict] = None
    created_at: Optional[datetime] = None

class Store(BaseModel):
    id: Optional[str] = None
    name: str
    brand_id: str
    description: str
    template: str  # modern-gallery, vintage-loft, luxury-palace, etc.
    products: Optional[List[str]] = None  # List of product IDs
    settings: Optional[dict] = None  # layout, lighting, music, etc.
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True

class UserAvatar(BaseModel):
    id: Optional[str] = None
    user_id: str
    scan_data_url: Optional[str] = None
    measurements: Optional[dict] = None
    body_type: Optional[str] = None  # pear, apple, hourglass, etc.
    created_at: Optional[datetime] = None

class TryOnSession(BaseModel):
    id: Optional[str] = None
    user_id: str
    store_id: str
    product_id: str
    avatar_id: Optional[str] = None
    created_at: Optional[datetime] = None

# In-memory storage for development (replace with database in production)
stores_db = []
products_db = []
avatars_db = []
tryon_sessions_db = []

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <head>
            <title>Aetherstore Engine</title>
        </head>
        <body>
            <h1>Welcome to Aetherstore Engine</h1>
            <p>The ultimate 3D fashion platform</p>
            <p>API documentation available at <a href="/docs">/docs</a></p>
            <p>Frontend available at <a href="/static">/static</a></p>
        </body>
    </html>
    """

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(), "version": "1.0.0"}

@app.get("/api/stores", response_model=List[Store])
async def get_stores():
    return stores_db

@app.post("/api/stores", response_model=Store)
async def create_store(store: Store):
    store.id = str(uuid.uuid4())
    store.created_at = datetime.now()
    store.updated_at = datetime.now()
    stores_db.append(store)
    return store

@app.get("/api/stores/{store_id}", response_model=Store)
async def get_store(store_id: str):
    for store in stores_db:
        if store.id == store_id:
            return store
    raise HTTPException(status_code=404, detail="Store not found")

@app.put("/api/stores/{store_id}", response_model=Store)
async def update_store(store_id: str, store: Store):
    for i, s in enumerate(stores_db):
        if s.id == store_id:
            store.id = store_id
            store.updated_at = datetime.now()
            stores_db[i] = store
            return store
    raise HTTPException(status_code=404, detail="Store not found")

@app.delete("/api/stores/{store_id}")
async def delete_store(store_id: str):
    for i, store in enumerate(stores_db):
        if store.id == store_id:
            del stores_db[i]
            return {"message": "Store deleted successfully"}
    raise HTTPException(status_code=404, detail="Store not found")

@app.get("/api/products", response_model=List[Product])
async def get_products():
    return products_db

@app.post("/api/products", response_model=Product)
async def create_product(product: Product):
    product.id = str(uuid.uuid4())
    product.created_at = datetime.now()
    products_db.append(product)
    return product

@app.get("/api/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    for product in products_db:
        if product.id == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")

@app.post("/api/upload/avatar", status_code=201)
async def upload_avatar_scan(file: UploadFile = File(...)):
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only images accepted.")
    
    # Save file to a temporary location
    file_location = f"backend/uploads/avatars/{file.filename}"
    os.makedirs("backend/uploads/avatars", exist_ok=True)
    
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "location": file_location
    }

@app.get("/api/avatars/{user_id}", response_model=UserAvatar)
async def get_user_avatar(user_id: str):
    for avatar in avatars_db:
        if avatar.user_id == user_id:
            return avatar
    raise HTTPException(status_code=404, detail="Avatar not found")

@app.post("/api/avatars", response_model=UserAvatar)
async def create_user_avatar(avatar: UserAvatar):
    avatar.id = str(uuid.uuid4())
    avatar.created_at = datetime.now()
    avatars_db.append(avatar)
    return avatar

@app.post("/api/tryon", response_model=TryOnSession)
async def create_tryon_session(session: TryOnSession):
    session.id = str(uuid.uuid4())
    session.created_at = datetime.now()
    tryon_sessions_db.append(session)
    return session

@app.get("/api/tryon/{session_id}", response_model=TryOnSession)
async def get_tryon_session(session_id: str):
    for session in tryon_sessions_db:
        if session.id == session_id:
            return session
    raise HTTPException(status_code=404, detail="Try-on session not found")


# Simplified recommendation endpoint
@app.get("/api/recommendations/{user_id}")
async def get_user_recommendations(user_id: str, n_recommendations: int = 10):
    """Simplified recommendations endpoint (simulated)"""
    recommendations = [
        {"product_id": f"prod_{i}", "score": 0.9 - (i * 0.05), "reason": "Based on similar users"}
        for i in range(1, n_recommendations + 1)
    ]
    
    return JSONResponse(content={"user_id": user_id, "recommendations": recommendations}, status_code=200)


# Simplified analytics endpoint
@app.get("/api/analytics/platform-overview")
async def get_platform_overview():
    """Simplified platform overview (simulated)"""
    overview = {
        "platform_kpis": {
            "total_users": len(set([s.user_id for s in tryon_sessions_db])),
            "total_products": len(products_db),
            "total_stores": len(stores_db),
            "total_events": len(tryon_sessions_db),
            "total_revenue": sum([p.price for p in products_db if hasattr(p, 'price')]) or 0
        }
    }
    return JSONResponse(content=overview, status_code=200)


if __name__ == "__main__":
    uvicorn.run("simplified_main:app", host="0.0.0.0", port=8000, reload=False)