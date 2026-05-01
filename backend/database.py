# database.py
# Database connection and session management for Aetherstore Engine

import os
from sqlalchemy import create_engine, text, pool
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aetherstore.db")

# SQLite-specific settings
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    # SQLite doesn't support pool_size
    pool_size = None
    max_overflow = None
else:
    pool_size = 20
    max_overflow = 30

# Engine arguments
engine_kwargs = {
    "connect_args": connect_args,
    "echo": False,  # Set to True for SQL debugging
}

if not DATABASE_URL.startswith("sqlite"):
    engine_kwargs["poolclass"] = pool.QueuePool
    engine_kwargs["pool_size"] = pool_size or 20
    engine_kwargs["max_overflow"] = max_overflow or 30
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_timeout"] = 30 # seconds to wait before giving up on getting a connection
    engine_kwargs["pool_recycle"] = 1800 # recycle connections after 30 minutes

# Create engine
engine = create_engine(DATABASE_URL, **engine_kwargs)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()

def get_db():
    """Dependency for FastAPI to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Alias for compatibility
get_db_session = get_db

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager for database sessions"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    try:
        # Import all models here to ensure they are registered
        from models import (
            User, Brand, Store, Product, ProductImage, UserAvatar, TryOnSession,
            ShoppingCart, CartItem, Order, OrderItem, StoreAnalytics, ProductAnalytics,
            AIModelPerformance, Asset, BrandTemplate, Friendship, SocialEvent, GroupSession, InventoryLog,
            UserStyleProfile, WardrobeItem
        )
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        # Don't raise exception to allow app to start for development

def get_db_health():
    """Check database health"""
    try:
        db = SessionLocal()
        # Try a simple query
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False