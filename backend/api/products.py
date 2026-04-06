# api/products.py
# Product management API endpoints for Aetherstore Engine

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import os
from sqlalchemy.orm import Session
from models import Product as DBProduct, ProductImage as DBProductImage, Brand as DBBrand, Store as DBStore
from crud import get_product, get_products_by_brand, get_products_by_store, create_product, update_product, delete_product
from crud import get_brand, get_store
from auth import get_current_active_user
from database import get_db_session
from models import InventoryLog

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
                           db: Session = Depends(get_db_session)):
    """Create a new product"""
    try:
        # Verify brand exists and user has permission
        db_brand = get_brand(db, product.brand_id)
        if not db_brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        # Verify store exists if provided
        if product.store_id:
            db_store = get_store(db, product.store_id)
            if not db_store:
                raise HTTPException(status_code=404, detail="Store not found")
        
        # In a real implementation, check if user owns the brand
        # For now, we'll allow creation if brand exists
        
        product_data = product.dict()
        db_product = create_product(db, product_data)
        return db_product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating product: {str(e)}")

@router.get("/", response_model=List[ProductResponse])
async def list_products(brand_id: Optional[str] = None, store_id: Optional[str] = None, 
                       category: Optional[str] = None, skip: int = 0, limit: int = 100,
                       current_user = Depends(get_current_active_user),
                       db: Session = Depends(get_db_session)):
    """List products with optional filtering"""
    try:
        query = db.query(Product)
        
        # Apply filters
        if brand_id:
            query = query.filter(Product.brand_id == brand_id)
        if store_id:
            query = query.filter(Product.store_id == store_id)
        if category:
            query = query.filter(Product.category == category)
        
        # Apply pagination
        products = query.offset(skip).limit(limit).all()
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing products: {str(e)}")

@router.get("/{product_id}", response_model=ProductResponse)
async def read_product(product_id: str, current_user = Depends(get_current_active_user),
                      db: Session = Depends(get_db_session)):
    """Get product by ID"""
    try:
        db_product = get_product(db, product_id)
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")
        return db_product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving product: {str(e)}")

@router.put("/{product_id}", response_model=ProductResponse)
async def update_existing_product(product_id: str, product: ProductUpdate, 
                                  current_user = Depends(get_current_active_user),
                                  db: Session = Depends(get_db_session)):
    """Update product by ID"""
    try:
        # Verify product exists
        db_product = get_product(db, product_id)
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # In a real implementation, check if user has permission to update product
        # For now, we'll allow updates
        
        update_data = product.dict(exclude_unset=True)
        if update_data:
            updated_product = update_product(db, product_id, update_data)
            if not updated_product:
                raise HTTPException(status_code=404, detail="Product not found")
            return updated_product
        return db_product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating product: {str(e)}")

@router.delete("/{product_id}", response_model=dict)
async def delete_existing_product(product_id: str, current_user = Depends(get_current_active_user),
                                db: Session = Depends(get_db_session)):
    """Delete product by ID"""
    try:
        # Verify product exists
        db_product = get_product(db, product_id)
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # In a real implementation, check if user has permission to delete product
        # For now, we'll allow deletion
        
        success = delete_product(db, product_id)
        if not success:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"message": "Product deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting product: {str(e)}")

# Product image endpoints
@router.post("/images/", response_model=ProductImageResponse, status_code=status.HTTP_201_CREATED)
async def upload_product_image(image_data: ProductImageCreate, current_user = Depends(get_current_active_user),
                              db: Session = Depends(get_db_session)):
    """Upload product image"""
    try:
        # Verify product exists
        db_product = get_product(db, image_data.product_id)
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # In a real implementation, this would save the image file and create database record
        # For now, we'll just create a database record
        
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading product image: {str(e)}")

@router.post("/upload-3d-model/{product_id}")
async def upload_3d_model(product_id: str, file: UploadFile = File(...), 
                          current_user = Depends(get_current_active_user),
                          db: Session = Depends(get_db_session)):
    """Upload 3D model for a product"""
    try:
        # Verify product exists
        db_product = get_product(db, product_id)
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Validate file type (should be GLB, GLTF, or other 3D formats)
        allowed_types = ['model/gltf-binary', 'model/gltf+json', 'application/octet-stream']
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Invalid file type. Only 3D models accepted.")
        
        # Create upload directory if it doesn't exist
        upload_dir = "uploads/3d_models"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_extension = os.path.splitext(file.filename)[1]
        file_path = os.path.join(upload_dir, f"{product_id}_{uuid.uuid4()}{file_extension}")
        
        with open(file_path, "wb+") as file_object:
            file_object.write(await file.read())
        
        # Update product with 3D model URL
        update_product(db, product_id, {"model_3d_url": file_path})
        
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "location": file_path
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading 3D model: {str(e)}")

@router.get("/{product_id}/images/", response_model=List[ProductImageResponse])
async def get_product_images(product_id: str, current_user = Depends(get_current_active_user),
                            db: Session = Depends(get_db_session)):
    """Get all images for a product"""
    try:
        # Verify product exists
        db_product = get_product(db, product_id)
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Get product images
        images = db.query(DBProductImage).filter(DBProductImage.product_id == product_id).all()
        return images
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving product images: {str(e)}")

# Merchant Inventory Management
class StockUpdate(BaseModel):
    product_id: str
    change_amount: int
    reason: str  # restock, manual_adjustment, damage

class BulkStockUpdate(BaseModel):
    updates: List[StockUpdate]

@router.post("/inventory/bulk-update")
async def bulk_update_inventory(
    data: BulkStockUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
):
    """Bulk update stock levels for multiple products"""
    results = []
    for update in data.updates:
        product = get_product(db, update.product_id)
        if not product:
            results.append({"product_id": update.product_id, "status": "not_found"})
            continue

        product.stock_quantity += update.change_amount

        # Log the change
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
async def get_low_stock_alerts(
    threshold: int = 5,
    brand_id: Optional[str] = None,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
):
    """Identify products with stock levels below the threshold"""
    query = db.query(DBProduct).filter(DBProduct.stock_quantity <= threshold)
    if brand_id:
        query = query.filter(DBProduct.brand_id == brand_id)

    low_stock_items = query.all()
    return [{
        "id": item.id,
        "name": item.name,
        "stock": item.stock_quantity,
        "brand_id": item.brand_id
    } for item in low_stock_items]