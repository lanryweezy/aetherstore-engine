# models.py
# SQLAlchemy models for Aetherstore Engine database tables

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, JSON, ForeignKey, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid
from typing import Optional
from datetime import datetime

# Helper function to generate UUIDs
def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    brands = relationship("Brand", back_populates="owner")
    avatars = relationship("UserAvatar", back_populates="user")
    tryon_sessions = relationship("TryOnSession", back_populates="user")
    shopping_carts = relationship("ShoppingCart", back_populates="user")
    orders = relationship("Order", back_populates="user")

class Brand(Base):
    __tablename__ = "brands"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    owner_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    description = Column(Text)
    logo_url = Column(String(500))
    settings = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    owner = relationship("User", back_populates="brands")
    stores = relationship("Store", back_populates="brand")
    products = relationship("Product", back_populates="brand")

class Store(Base):
    __tablename__ = "stores"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    brand_id = Column(UUID(as_uuid=False), ForeignKey("brands.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    template = Column(String(100), default="modern-gallery")
    lighting_preset = Column(String(100), default="studio") # studio, cinematic, sunlight, neon, warm, minimalist
    description = Column(Text)
    settings = Column(JSON, default={})
    scene_state = Column(JSON, default={}) # 3D Layout: coords and rotations for props
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    brand = relationship("Brand", back_populates="stores")
    products = relationship("Product", back_populates="store")
    tryon_sessions = relationship("TryOnSession", back_populates="store")
    analytics = relationship("StoreAnalytics", back_populates="store")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    brand_id = Column(UUID(as_uuid=False), ForeignKey("brands.id", ondelete="CASCADE"))
    store_id = Column(UUID(as_uuid=False), ForeignKey("stores.id", ondelete="SET NULL"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category = Column(String(100))
    subcategory = Column(String(100))
    size_chart = Column(JSON)
    colors = Column(JSON)
    materials = Column(JSON)
    dimensions = Column(JSON)
    care_instructions = Column(Text)
    model_3d_url = Column(String(500))
    textures_urls = Column(JSON)
    physics_properties = Column(JSON)
    stock_quantity = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    brand = relationship("Brand", back_populates="products")
    store = relationship("Store", back_populates="products")
    images = relationship("ProductImage", back_populates="product")
    tryon_sessions = relationship("TryOnSession", back_populates="product")
    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
    analytics = relationship("ProductAnalytics", back_populates="product")

class ProductImage(Base):
    __tablename__ = "product_images"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    product_id = Column(UUID(as_uuid=False), ForeignKey("products.id", ondelete="CASCADE"))
    image_url = Column(String(500), nullable=False)
    alt_text = Column(String(255))
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="images")

class UserAvatar(Base):
    __tablename__ = "user_avatars"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"))
    scan_data_url = Column(String(500))
    measurements = Column(JSON)
    body_type = Column(String(50))
    avatar_3d_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="avatars")
    tryon_sessions = relationship("TryOnSession", back_populates="avatar")

class TryOnSession(Base):
    __tablename__ = "tryon_sessions"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"))
    store_id = Column(UUID(as_uuid=False), ForeignKey("stores.id", ondelete="CASCADE"))
    product_id = Column(UUID(as_uuid=False), ForeignKey("products.id", ondelete="CASCADE"))
    avatar_id = Column(UUID(as_uuid=False), ForeignKey("user_avatars.id", ondelete="SET NULL"))
    session_data = Column(JSON)
    fit_analysis = Column(JSON)
    duration_seconds = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="tryon_sessions")
    store = relationship("Store", back_populates="tryon_sessions")
    product = relationship("Product", back_populates="tryon_sessions")
    avatar = relationship("UserAvatar", back_populates="tryon_sessions")

class ShoppingCart(Base):
    __tablename__ = "shopping_carts"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="shopping_carts")
    items = relationship("CartItem", back_populates="cart")

class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    cart_id = Column(UUID(as_uuid=False), ForeignKey("shopping_carts.id", ondelete="CASCADE"))
    product_id = Column(UUID(as_uuid=False), ForeignKey("products.id", ondelete="CASCADE"))
    quantity = Column(Integer, default=1)
    selected_size = Column(String(10))
    selected_color = Column(String(50))
    price_at_time = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    cart = relationship("ShoppingCart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"))
    cart_id = Column(UUID(as_uuid=False), ForeignKey("shopping_carts.id", ondelete="SET NULL"))
    total_amount = Column(Float, nullable=False)
    status = Column(String(50), default="pending")
    shipping_address = Column(JSON)
    billing_address = Column(JSON)
    payment_method = Column(String(50))
    payment_status = Column(String(50), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    order_id = Column(UUID(as_uuid=False), ForeignKey("orders.id", ondelete="CASCADE"))
    product_id = Column(UUID(as_uuid=False), ForeignKey("products.id", ondelete="CASCADE"))
    quantity = Column(Integer, nullable=False)
    price_at_time = Column(Float)
    size = Column(String(10))
    color = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

class StoreAnalytics(Base):
    __tablename__ = "store_analytics"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    store_id = Column(UUID(as_uuid=False), ForeignKey("stores.id", ondelete="CASCADE"))
    date = Column(DateTime(timezone=False), nullable=False)
    page_views = Column(Integer, default=0)
    unique_visitors = Column(Integer, default=0)
    session_duration_seconds = Column(Integer, default=0)
    tryon_sessions_count = Column(Integer, default=0)
    add_to_cart_count = Column(Integer, default=0)
    purchase_count = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    store = relationship("Store", back_populates="analytics")

class ProductAnalytics(Base):
    __tablename__ = "product_analytics"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    product_id = Column(UUID(as_uuid=False), ForeignKey("products.id", ondelete="CASCADE"))
    date = Column(DateTime(timezone=False), nullable=False)
    views = Column(Integer, default=0)
    tryon_count = Column(Integer, default=0)
    add_to_cart_count = Column(Integer, default=0)
    purchase_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="analytics")

class AIModelPerformance(Base):
    __tablename__ = "ai_model_performance"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    model_name = Column(String(255), nullable=False)
    input_data = Column(JSON)
    output_data = Column(JSON)
    confidence_score = Column(Float)
    execution_time_ms = Column(Integer)
    feedback = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    owner_id = Column(UUID(as_uuid=False))
    owner_type = Column(String(20))
    asset_type = Column(String(50))
    file_url = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    dimensions = Column(JSON)
    status = Column(String(20), default="active")
    asset_metadata = Column(JSON)  # Changed from 'metadata' to avoid reserved keyword
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class BrandTemplate(Base):
    __tablename__ = "brand_templates"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    settings = Column(JSON, default={})
    preview_image_url = Column(String(500))
    is_public = Column(Boolean, default=False)
    created_by = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Friendship(Base):
    __tablename__ = "friendships"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"))
    friend_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"))
    status = Column(String(50), default="accepted") # accepted, pending, blocked
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SocialEvent(Base):
    __tablename__ = "social_events"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"))
    target_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    event_type = Column(String(50), nullable=False)
    data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class GroupSession(Base):
    __tablename__ = "group_sessions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    creator_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"))
    store_id = Column(UUID(as_uuid=False), ForeignKey("stores.id", ondelete="CASCADE"))
    status = Column(String(50), default="planned") # planned, active, completed
    settings = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))

class InventoryLog(Base):
    __tablename__ = "inventory_logs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    product_id = Column(UUID(as_uuid=False), ForeignKey("products.id", ondelete="CASCADE"))
    change_amount = Column(Integer, nullable=False)
    reason = Column(String(255)) # purchase, restock, return, adjustment
    remaining_stock = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserStyleProfile(Base):
    __tablename__ = "user_style_profiles"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    body_type = Column(String(50))
    height = Column(Float)
    age = Column(Integer)
    style_preferences = Column(JSON) # List of styles
    color_preferences = Column(JSON) # List of colors
    size_preferences = Column(JSON) # category -> size
    budget_level = Column(String(50))
    lifestyle = Column(String(100))
    seasonal_preferences = Column(JSON)
    fashion_goals = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class WardrobeItem(Base):
    __tablename__ = "wardrobe_items"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    category = Column(String(100))
    color = Column(String(50))
    brand = Column(String(100))
    purchase_date = Column(DateTime(timezone=True), server_default=func.now())
    times_worn = Column(Integer, default=0)
    condition = Column(String(50), default="excellent")
    style_tags = Column(JSON)
    is_equipped = Column(Boolean, default=False) # Whether it's currently worn by avatar
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class StyleBoard(Base):
    __tablename__ = "style_boards"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    item_ids = Column(JSON) # List of WardrobeItem or Product IDs
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class UserActivity(Base):
    __tablename__ = "user_activities"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"))
    activity_type = Column(String(50), nullable=False) # view_product, visit_store, try_on, search
    product_id = Column(UUID(as_uuid=False), ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    store_id = Column(UUID(as_uuid=False), ForeignKey("stores.id", ondelete="SET NULL"), nullable=True)
    metadata_json = Column(JSON, default={})
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class UserLoyalty(Base):
    __tablename__ = "user_loyalty"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    brand_id = Column(UUID(as_uuid=False), ForeignKey("brands.id", ondelete="CASCADE"), nullable=True) # If multi-brand, null means global
    points_balance = Column(Integer, default=0)
    tier = Column(String(50), default="bronze") # bronze, silver, gold, platinum
    total_earned = Column(Integer, default=0)
    last_activity = Column(DateTime(timezone=True), server_default=func.now())

class LoyaltyTransaction(Base):
    __tablename__ = "loyalty_transactions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"))
    amount = Column(Integer, nullable=False) # Positive for earn, negative for redeem
    reason = Column(String(255)) # purchase, review, referral, social_share
    metadata_json = Column(JSON, default={})
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class ProductReview(Base):
    __tablename__ = "product_reviews"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"))
    product_id = Column(UUID(as_uuid=False), ForeignKey("products.id", ondelete="CASCADE"))
    rating = Column(Integer, nullable=False) # 1-5
    comment = Column(Text)
    is_verified_purchase = Column(Boolean, default=False)
    helpful_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())