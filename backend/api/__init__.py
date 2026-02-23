# api/__init__.py
# API routers for Aetherstore Engine

from fastapi import APIRouter
from . import users, stores, products, avatars, tryon, payments, orders, subscriptions

# Create main API router
api_router = APIRouter(prefix="/api")

# Include all sub-routers
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(stores.router, prefix="/stores", tags=["stores"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(avatars.router, prefix="/avatars", tags=["avatars"])
api_router.include_router(tryon.router, prefix="/tryon", tags=["tryon"])
api_router.include_router(payments.router, tags=["payments"])
api_router.include_router(orders.router, tags=["orders"])
api_router.include_router(subscriptions.router, tags=["subscriptions"])

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "now"}

# Version info
__version__ = "1.0.0"
__author__ = "Aetherstore Engine Team"