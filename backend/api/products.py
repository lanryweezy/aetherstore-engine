# api/products.py
# Product management API endpoints for Aetherstore Engine

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import os
from sqlalchemy import String, func
from sqlalchemy.orm import Session
from models import Product, ProductImage, Brand, Store, InventoryLog
from crud import get_product, get_products_by_brand, get_products_by_store, create_product, update_product, delete_product
from crud import get_brand, get_store
from auth import get_current_active_user
from database import get_db
from .subscriptions import SUBSCRIPTION_PLANS

router = APIRouter()

# Pydantic models for request/response
class ProductCreate(BaseModel):
    brand_id: str
    store_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    subcategory: Optional[str] = None
    size_chart: Optional[Dict[str, Any]] = {}
    colors: Optional[List[str]] = []
    materials: Optional[Dict[str, Any]] = {}
    dimensions: Optional[Dict[str, Any]] = {}
    care_instructions: Optional[str] = None
    model_3d_url: Optional[str] = None
    textures_urls: Optional[List[str]] = []
    physics_properties: Optional[Dict[str, Any]] = {}
    stock_quantity: Optional[int] = 0

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    size_chart: Optional[Dict[str, Any]] = None
    colors: Optional[List[str]] = None
    materials: Optional[Dict[str, Any]] = None
    dimensions: Optional[Dict[str, Any]] = None
    care_instructions: Optional[str] = None
    model_3d_url: Optional[str] = None
    textures_urls: Optional[List[str]] = None
    physics_properties: Optional[Dict[str, Any]] = None
    stock_quantity: Optional[int] = None
    is_active: Optional[bool] = None

class ProductResponse(BaseModel):
    id: str
    brand_id: str
    store_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    subcategory: Optional[str] = None
    size_chart: Optional[Dict[str, Any]] = {}
    colors: Optional[List[str]] = []
    materials: Optional[Dict[str, Any]] = {}
    dimensions: Optional[Dict[str, Any]] = {}
    care_instructions: Optional[str] = None
    model_3d_url: Optional[str] = None
    textures_urls: Optional[List[str]] = []
    physics_properties: Optional[Dict[str, Any]] = {}
    stock_quantity: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True

class ProductImageCreate(BaseModel):
    product_id: str
    image_url: str
    alt_text: Optional[str] = None
    is_primary: Optional[bool] = False

class ProductImageResponse(BaseModel):
    id: str
    product_id: str
    image_url: str
    alt_text: Optional[str] = None
    is_primary: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Product endpoints
@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_new_product(product: ProductCreate, current_user = Depends(get_current_active_user),
                           db: Session = Depends(get_db)):
    """Create a new product with feature gating"""
    # Verify brand exists and user has permission
    db_brand = get_brand(db, product.brand_id)
    if not db_brand or db_brand.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to manage this brand")

    # FEATURE GATING: Check product limits
    subscription = db_brand.settings.get("subscription", {})
    plan_name = subscription.get("plan", "starter")
    plan_limits = SUBSCRIPTION_PLANS.get(plan_name, SUBSCRIPTION_PLANS["starter"])

    current_products_count = db.query(Product).filter(Product.brand_id == db_brand.id).count()
    limit = plan_limits["features"]["products"]

    if limit != "unlimited" and current_products_count >= limit:
        raise HTTPException(
            status_code=403,
            detail=f"Product limit reached for {plan_name} plan. Upgrade to add more products."
        )

    product_data = product.dict()
    db_product = create_product(db, product_data)
    return db_product

@router.get("/", response_model=List[ProductResponse])
async def list_products(brand_id: Optional[str] = None, store_id: Optional[str] = None, 
                       category: Optional[str] = None, skip: int = 0, limit: int = 100,
                       current_user = Depends(get_current_active_user),
                       db: Session = Depends(get_db)):
    """List products with optional filtering"""
    query = db.query(Product)
    if brand_id:
        query = query.filter(Product.brand_id == brand_id)
    if store_id:
        query = query.filter(Product.store_id == store_id)
    if category:
        query = query.filter(Product.category == category)
    return query.offset(skip).limit(limit).all()

@router.get("/{product_id}", response_model=ProductResponse)
async def read_product(product_id: str, db: Session = Depends(get_db)):
    """Get product by ID"""
    db_product = get_product(db, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.put("/{product_id}", response_model=ProductResponse)
async def update_existing_product(product_id: str, product: ProductUpdate, 
                                  current_user = Depends(get_current_active_user),
                                  db: Session = Depends(get_db)):
    db_product = get_product(db, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    db_brand = get_brand(db, db_product.brand_id)
    if db_brand.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    update_data = product.dict(exclude_unset=True)
    return update_product(db, product_id, update_data)

@router.delete("/{product_id}")
async def delete_existing_product(product_id: str, current_user = Depends(get_current_active_user),
                                db: Session = Depends(get_db)):
    db_product = get_product(db, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    db_brand = get_brand(db, db_product.brand_id)
    if db_brand.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    delete_product(db, product_id)
    return {"message": "Product deleted"}

# Product image endpoints
@router.post("/images/", response_model=ProductImageResponse, status_code=status.HTTP_201_CREATED)
async def upload_product_image(image_data: ProductImageCreate, current_user = Depends(get_current_active_user),
                              db: Session = Depends(get_db)):
    db_product = get_product(db, image_data.product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    db_image = ProductImage(
        id=str(uuid.uuid4()),
        product_id=image_data.product_id,
        image_url=image_data.image_url,
        alt_text=image_data.alt_text,
        is_primary=image_data.is_primary,
        created_at=datetime.utcnow()
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

def process_3d_model_background(product_id: str, raw_path: str, optimized_path: str):
    """Background task to optimize 3D model and update the database."""
    from database import SessionLocal
    import logging
    logger = logging.getLogger(__name__)

    try:
        from asset_processor_3d import optimize_3d_model, OptimizationLevel
        # Decimate mesh and compress textures automatically
        result = optimize_3d_model(raw_path, optimized_path, OptimizationLevel.MEDIUM)
        if result.success:
            final_path = optimized_path
            try:
                os.remove(raw_path) # Clean up raw file
            except OSError:
                pass
        else:
            final_path = raw_path # Fallback to raw if optimization fails
            logger.warning(f"3D Optimization failed for {product_id}: {result.error_message}")
    except Exception as e:
        final_path = raw_path
        logger.error(f"Error in 3D pipeline for {product_id}: {e}")

    # Create a fresh database session for the background task
    db = SessionLocal()
    try:
        from crud import update_product
        update_product(db, product_id, {"model_3d_url": final_path})
        db.commit()
    except Exception as e:
        logger.error(f"Failed to update product {product_id} after optimization: {e}")
    finally:
        db.close()

from fastapi import Form
import json
import base64
from PIL import Image
import io
from pathlib import Path

@router.post("/upload-3d-model/{product_id}")
async def upload_3d_model(product_id: str,
                          background_tasks: BackgroundTasks,
                          file: UploadFile = File(...),
                          thumbnails: Optional[str] = Form(None),
                          current_user = Depends(get_current_active_user),
                          db: Session = Depends(get_db)):
    """Upload and schedule automatic optimization of a 3D model for the web"""
    db_product = get_product(db, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    allowed_types = ['model/gltf-binary', 'model/gltf+json', 'application/octet-stream']
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type")

    upload_dir = "uploads/3d_models"
    os.makedirs(upload_dir, exist_ok=True)
    raw_path = os.path.join(upload_dir, f"raw_{product_id}_{uuid.uuid4()}{os.path.splitext(file.filename)[1]}")
    optimized_path = os.path.join(upload_dir, f"opt_{product_id}_{uuid.uuid4()}.glb")

    # Save original file
    with open(raw_path, "wb+") as file_object:
        file_object.write(await file.read())

    # Handle client-generated thumbnails if provided
    if thumbnails:
        try:
            thumbs_data = json.loads(thumbnails)
            thumb_dir = Path(raw_path).parent / "thumbnails"
            thumb_dir.mkdir(exist_ok=True)

            for view_name, base64_data in thumbs_data.items():
                if base64_data and base64_data.startswith("data:image"):
                    # Extract the base64 string
                    header, encoded = base64_data.split(",", 1)
                    image_data = base64.b64decode(encoded)
                    image = Image.open(io.BytesIO(image_data))

                    thumb_path = thumb_dir / f"{Path(raw_path).stem}_{view_name}.png"
                    image.save(thumb_path, "PNG")
                    logger.info(f"Saved client-generated thumbnail to {thumb_path}")
        except Exception as e:
            logger.error(f"Failed to process client-generated thumbnails: {e}")

    # Update product immediately to show the raw file while processing
    update_product(db, product_id, {"model_3d_url": raw_path})

    # TRIGGER AUTO-OPTIMIZATION IN BACKGROUND
    background_tasks.add_task(process_3d_model_background, product_id, raw_path, optimized_path)

    return {
        "location": raw_path,
        "status": "processing",
        "message": "3D model uploaded and is being optimized in the background."
    }

@router.get("/{product_id}/images/", response_model=List[ProductImageResponse])
async def get_product_images(product_id: str, db: Session = Depends(get_db)):
    images = db.query(ProductImage).filter(ProductImage.product_id == product_id).all()
    return images

# Merchant Inventory Management
class StockUpdate(BaseModel):
    product_id: str
    change_amount: int
    reason: str  # restock, manual_adjustment, damage

class BulkStockUpdate(BaseModel):
    updates: List[StockUpdate]

@router.post("/inventory/bulk-update")
async def bulk_update_inventory(data: BulkStockUpdate, current_user = Depends(get_current_active_user), db: Session = Depends(get_db)):
    results = []
    for update in data.updates:
        product = get_product(db, update.product_id)
        if not product:
            results.append({"product_id": update.product_id, "status": "not_found"})
            continue

        product.stock_quantity += update.change_amount
        log = InventoryLog(
            product_id=product.id,
            change_amount=update.change_amount,
            reason=update.reason,
            remaining_stock=product.stock_quantity
        )
        db.add(log)
        results.append({"product_id": update.product_id, "status": "updated", "new_stock": product.stock_quantity})

    db.commit()
    return {"results": results}

@router.get("/inventory/low-stock")
async def get_low_stock_alerts(threshold: int = 5, brand_id: Optional[str] = None, current_user = Depends(get_current_active_user), db: Session = Depends(get_db)):
    query = db.query(Product).filter(Product.stock_quantity <= threshold)
    if brand_id:
        query = query.filter(Product.brand_id == brand_id)
    low_stock_items = query.all()
    return [{"id": item.id, "name": item.name, "stock": item.stock_quantity, "brand_id": item.brand_id} for item in low_stock_items]

@router.get("/search/advanced", response_model=List[ProductResponse])
async def search_products_advanced(
    q: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    category: Optional[str] = None,
    material: Optional[str] = None,
    color: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Advanced search with multiple filters and keyword matching"""
    query = db.query(Product)

    if q:
        search_filter = (Product.name.ilike(f"%{q}%")) | (Product.description.ilike(f"%{q}%"))
        query = query.filter(search_filter)

    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if category:
        query = query.filter(Product.category == category)

    if material:
        query = query.filter(Product.materials.cast(String).ilike(f"%{material}%"))

    if color:
        query = query.filter(Product.colors.cast(String).ilike(f"%{color}%"))

    return query.all()

# Social Proof & Reviews System
from models import ProductReview
class ReviewCreate(BaseModel):
    product_id: str
    rating: int
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: str
    user_id: str
    product_id: str
    rating: int
    comment: Optional[str] = None
    is_verified_purchase: bool
    helpful_count: int
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/{product_id}/reviews", response_model=ReviewResponse)
async def create_review(product_id: str, review_in: ReviewCreate, current_user = Depends(get_current_active_user), db: Session = Depends(get_db)):
    # Check if user already reviewed
    existing = db.query(ProductReview).filter(ProductReview.user_id == current_user.id, ProductReview.product_id == product_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already reviewed this product")

    # Verify if user actually purchased it (Mock check)
    from models import Order, OrderItem
    has_purchased = db.query(OrderItem).join(Order).filter(
        Order.user_id == current_user.id,
        OrderItem.product_id == product_id,
        Order.status == "completed"
    ).first() is not None

    new_review = ProductReview(
        user_id=current_user.id,
        product_id=product_id,
        rating=review_in.rating,
        comment=review_in.comment,
        is_verified_purchase=has_purchased
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review

@router.get("/{product_id}/reviews", response_model=List[ReviewResponse])
async def list_product_reviews(product_id: str, db: Session = Depends(get_db)):
    return db.query(ProductReview).filter(ProductReview.product_id == product_id).all()

@router.get("/{product_id}/rating")
async def get_product_rating(product_id: str, db: Session = Depends(get_db)):
    stats = db.query(
        func.avg(ProductReview.rating).label('average'),
        func.count(ProductReview.id).label('count')
    ).filter(ProductReview.product_id == product_id).first()
    return {"average_rating": float(stats.average) if stats.average else 0, "review_count": stats.count}
