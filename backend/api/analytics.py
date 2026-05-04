# api/analytics.py
from fastapi import APIRouter, Depends, Query
from typing import Optional
from analytics_engine import analytics_service

router = APIRouter()

@router.get("/heatmap/{store_id}")
async def get_store_heatmap(store_id: str):
    """Retrieve 3D spatial interaction heatmap for a store"""
    return await analytics_service.get_insights("heatmap", store_id=store_id)

@router.get("/funnel")
async def get_funnel(store_id: Optional[str] = None, product_id: Optional[str] = None):
    """Get the conversion funnel for a store or product"""
    # Funnel logic is inside analytics_engine, accessed through the service if needed
    return await analytics_service.analytics_engine.get_conversion_funnel(store_id=store_id, product_id=product_id)

@router.get("/overview")
async def get_overview():
    """Get overall platform performance"""
    return analytics_service.analytics_engine.get_platform_overview()
