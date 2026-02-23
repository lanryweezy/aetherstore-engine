# crud.py
# CRUD operations for Aetherstore Engine database models

from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from models import User, Brand, Store, Product, ProductImage, UserAvatar, TryOnSession
from models import ShoppingCart, CartItem, Order, OrderItem, StoreAnalytics, ProductAnalytics
from models import AIModelPerformance, Asset, BrandTemplate
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# User CRUD operations
def get_user(db: Session, user_id: str) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user_data: Dict[str, Any]) -> User:
    """Create a new user"""
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: str, user_data: Dict[str, Any]) -> Optional[User]:
    """Update user by ID"""
    db_user = get_user(db, user_id)
    if db_user:
        for key, value in user_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: str) -> bool:
    """Delete user by ID"""
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

# Brand CRUD operations
def get_brand(db: Session, brand_id: str) -> Optional[Brand]:
    """Get brand by ID"""
    return db.query(Brand).filter(Brand.id == brand_id).first()

def get_brands_by_owner(db: Session, owner_user_id: str) -> List[Brand]:
    """Get all brands owned by a user"""
    return db.query(Brand).filter(Brand.owner_user_id == owner_user_id).all()

def create_brand(db: Session, brand_data: Dict[str, Any]) -> Brand:
    """Create a new brand"""
    db_brand = Brand(**brand_data)
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    return db_brand

def update_brand(db: Session, brand_id: str, brand_data: Dict[str, Any]) -> Optional[Brand]:
    """Update brand by ID"""
    db_brand = get_brand(db, brand_id)
    if db_brand:
        for key, value in brand_data.items():
            setattr(db_brand, key, value)
        db.commit()
        db.refresh(db_brand)
    return db_brand

def delete_brand(db: Session, brand_id: str) -> bool:
    """Delete brand by ID"""
    db_brand = get_brand(db, brand_id)
    if db_brand:
        db.delete(db_brand)
        db.commit()
        return True
    return False

# Store CRUD operations
def get_store(db: Session, store_id: str) -> Optional[Store]:
    """Get store by ID"""
    return db.query(Store).filter(Store.id == store_id).first()

def get_stores_by_brand(db: Session, brand_id: str) -> List[Store]:
    """Get all stores for a brand"""
    return db.query(Store).filter(Store.brand_id == brand_id).all()

def create_store(db: Session, store_data: Dict[str, Any]) -> Store:
    """Create a new store"""
    db_store = Store(**store_data)
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    return db_store

def update_store(db: Session, store_id: str, store_data: Dict[str, Any]) -> Optional[Store]:
    """Update store by ID"""
    db_store = get_store(db, store_id)
    if db_store:
        for key, value in store_data.items():
            setattr(db_store, key, value)
        db.commit()
        db.refresh(db_store)
    return db_store

def delete_store(db: Session, store_id: str) -> bool:
    """Delete store by ID"""
    db_store = get_store(db, store_id)
    if db_store:
        db.delete(db_store)
        db.commit()
        return True
    return False

# Product CRUD operations
def get_product(db: Session, product_id: str) -> Optional[Product]:
    """Get product by ID"""
    return db.query(Product).filter(Product.id == product_id).first()

def get_products_by_brand(db: Session, brand_id: str) -> List[Product]:
    """Get all products for a brand"""
    return db.query(Product).filter(Product.brand_id == brand_id).all()

def get_products_by_store(db: Session, store_id: str) -> List[Product]:
    """Get all products for a store"""
    return db.query(Product).filter(Product.store_id == store_id).all()

def create_product(db: Session, product_data: Dict[str, Any]) -> Product:
    """Create a new product"""
    db_product = Product(**product_data)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: str, product_data: Dict[str, Any]) -> Optional[Product]:
    """Update product by ID"""
    db_product = get_product(db, product_id)
    if db_product:
        for key, value in product_data.items():
            setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: str) -> bool:
    """Delete product by ID"""
    db_product = get_product(db, product_id)
    if db_product:
        db.delete(db_product)
        db.commit()
        return True
    return False

# User Avatar CRUD operations
def get_user_avatar(db: Session, user_id: str) -> Optional[UserAvatar]:
    """Get user avatar by user ID"""
    return db.query(UserAvatar).filter(UserAvatar.user_id == user_id).first()

def create_user_avatar(db: Session, avatar_data: Dict[str, Any]) -> UserAvatar:
    """Create a new user avatar"""
    db_avatar = UserAvatar(**avatar_data)
    db.add(db_avatar)
    db.commit()
    db.refresh(db_avatar)
    return db_avatar

def update_user_avatar(db: Session, avatar_id: str, avatar_data: Dict[str, Any]) -> Optional[UserAvatar]:
    """Update user avatar by ID"""
    db_avatar = db.query(UserAvatar).filter(UserAvatar.id == avatar_id).first()
    if db_avatar:
        for key, value in avatar_data.items():
            setattr(db_avatar, key, value)
        db.commit()
        db.refresh(db_avatar)
    return db_avatar

def delete_user_avatar(db: Session, avatar_id: str) -> bool:
    """Delete user avatar by ID"""
    db_avatar = db.query(UserAvatar).filter(UserAvatar.id == avatar_id).first()
    if db_avatar:
        db.delete(db_avatar)
        db.commit()
        return True
    return False

# Try-On Session CRUD operations
def get_tryon_session(db: Session, session_id: str) -> Optional[TryOnSession]:
    """Get try-on session by ID"""
    return db.query(TryOnSession).filter(TryOnSession.id == session_id).first()

def create_tryon_session(db: Session, session_data: Dict[str, Any]) -> TryOnSession:
    """Create a new try-on session"""
    db_session = TryOnSession(**session_data)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def update_tryon_session(db: Session, session_id: str, session_data: Dict[str, Any]) -> Optional[TryOnSession]:
    """Update try-on session by ID"""
    db_session = get_tryon_session(db, session_id)
    if db_session:
        for key, value in session_data.items():
            setattr(db_session, key, value)
        db.commit()
        db.refresh(db_session)
    return db_session

def delete_tryon_session(db: Session, session_id: str) -> bool:
    """Delete try-on session by ID"""
    db_session = get_tryon_session(db, session_id)
    if db_session:
        db.delete(db_session)
        db.commit()
        return True
    return False

# Analytics CRUD operations
def create_store_analytics(db: Session, analytics_data: Dict[str, Any]) -> StoreAnalytics:
    """Create store analytics record"""
    db_analytics = StoreAnalytics(**analytics_data)
    db.add(db_analytics)
    db.commit()
    db.refresh(db_analytics)
    return db_analytics

def create_product_analytics(db: Session, analytics_data: Dict[str, Any]) -> ProductAnalytics:
    """Create product analytics record"""
    db_analytics = ProductAnalytics(**analytics_data)
    db.add(db_analytics)
    db.commit()
    db.refresh(db_analytics)
    return db_analytics

def get_store_analytics(db: Session, store_id: str, date: datetime) -> Optional[StoreAnalytics]:
    """Get store analytics for a specific date"""
    return db.query(StoreAnalytics).filter(
        StoreAnalytics.store_id == store_id,
        StoreAnalytics.date == date
    ).first()

def get_product_analytics(db: Session, product_id: str, date: datetime) -> Optional[ProductAnalytics]:
    """Get product analytics for a specific date"""
    return db.query(ProductAnalytics).filter(
        ProductAnalytics.product_id == product_id,
        ProductAnalytics.date == date
    ).first()

# Asset CRUD operations
def get_asset(db: Session, asset_id: str) -> Optional[Asset]:
    """Get asset by ID"""
    return db.query(Asset).filter(Asset.id == asset_id).first()

def create_asset(db: Session, asset_data: Dict[str, Any]) -> Asset:
    """Create a new asset"""
    db_asset = Asset(**asset_data)
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset

def update_asset(db: Session, asset_id: str, asset_data: Dict[str, Any]) -> Optional[Asset]:
    """Update asset by ID"""
    db_asset = get_asset(db, asset_id)
    if db_asset:
        for key, value in asset_data.items():
            setattr(db_asset, key, value)
        db.commit()
        db.refresh(db_asset)
    return db_asset

def delete_asset(db: Session, asset_id: str) -> bool:
    """Delete asset by ID"""
    db_asset = get_asset(db, asset_id)
    if db_asset:
        db.delete(db_asset)
        db.commit()
        return True
    return False

# AI Model Performance CRUD operations
def create_ai_model_performance(db: Session, performance_data: Dict[str, Any]) -> AIModelPerformance:
    """Create AI model performance record"""
    db_performance = AIModelPerformance(**performance_data)
    db.add(db_performance)
    db.commit()
    db.refresh(db_performance)
    return db_performance

# Shopping Cart CRUD operations
def get_user_cart(db: Session, user_id: str) -> Optional[ShoppingCart]:
    """Get user's shopping cart"""
    return db.query(ShoppingCart).filter(ShoppingCart.user_id == user_id).first()

def create_shopping_cart(db: Session, cart_data: Dict[str, Any]) -> ShoppingCart:
    """Create a new shopping cart"""
    db_cart = ShoppingCart(**cart_data)
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    return db_cart

def add_item_to_cart(db: Session, cart_item_data: Dict[str, Any]) -> CartItem:
    """Add item to shopping cart"""
    db_cart_item = CartItem(**cart_item_data)
    db.add(db_cart_item)
    db.commit()
    db.refresh(db_cart_item)
    return db_cart_item

def remove_item_from_cart(db: Session, cart_item_id: str) -> bool:
    """Remove item from shopping cart"""
    db_cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
    if db_cart_item:
        db.delete(db_cart_item)
        db.commit()
        return True
    return False

# Order CRUD operations
def get_order(db: Session, order_id: str) -> Optional[Order]:
    """Get order by ID"""
    return db.query(Order).filter(Order.id == order_id).first()

def create_order(db: Session, order_data: Dict[str, Any]) -> Order:
    """Create a new order"""
    db_order = Order(**order_data)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def update_order_status(db: Session, order_id: str, status: str) -> Optional[Order]:
    """Update order status"""
    db_order = get_order(db, order_id)
    if db_order:
        db_order.status = status
        db.commit()
        db.refresh(db_order)
    return db_order

# Utility functions
def get_or_create_user_cart(db: Session, user_id: str) -> ShoppingCart:
    """Get user's cart or create a new one if it doesn't exist"""
    cart = get_user_cart(db, user_id)
    if not cart:
        cart = create_shopping_cart(db, {"user_id": user_id})
    return cart