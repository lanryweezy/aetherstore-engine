# api/analytics.py
from fastapi import APIRouter, Depends, Query
from typing import Optional
from analytics_engine import AnalyticsEngine

router = APIRouter()
analytics_engine = AnalyticsEngine()

@router.get("/funnel")
async def get_funnel(store_id: Optional[str] = None, product_id: Optional[str] = None):
    """Get the conversion funnel for a store or product"""
    return analytics_engine.get_conversion_funnel(store_id=store_id, product_id=product_id)

@router.get("/heatmap/{store_id}")
async def get_heatmap(store_id: str):
    """Get heatmap and spatial analytics for a store"""
    return analytics_engine.get_heatmap_data(store_id)

@router.get("/overview")
async def get_overview():
    """Get overall platform performance"""
    return analytics_engine.get_platform_overview()
