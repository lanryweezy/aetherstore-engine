# Advanced Analytics and Insights Engine for Aetherstore Engine
# Provides business intelligence, user behavior analysis, and performance metrics

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
import json
from collections import defaultdict
from sqlalchemy.orm import Session
from database import SessionLocal
from models import StoreAnalytics, ProductAnalytics, TryOnSession, Order, OrderItem
from sqlalchemy import func

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventType(Enum):
    PRODUCT_VIEW = "product_view"
    TRY_ON = "try_on"
    ADD_TO_CART = "add_to_cart"
    PURCHASE = "purchase"
    CART_ABANDON = "cart_abandon"
    PAGE_VIEW = "page_view"
    TIME_SPENT = "time_spent"

@dataclass
class EventData:
    event_type: EventType
    user_id: str
    product_id: str
    timestamp: datetime
    session_id: str
    store_id: str
    additional_data: Dict = None

@dataclass
class UserBehaviorMetrics:
    total_sessions: int
    avg_session_duration: float  # in minutes
    page_views: int
    products_viewed: int
    try_on_count: int
    add_to_cart_count: int
    purchase_count: int
    conversion_rate: float
    avg_order_value: float
    last_active: datetime

@dataclass
class ProductPerformanceMetrics:
    views: int
    try_ons: int
    add_to_cart: int
    purchases: int
    conversion_rate: float
    avg_rating: float
    revenue: float
    popularity_score: float
    trend: str  # up, down, stable

@dataclass
class StorePerformanceMetrics:
    total_visitors: int
    avg_time_spent: float  # in minutes
    bounce_rate: float
    conversion_rate: float
    total_revenue: float
    cart_abandonment_rate: float
    popular_products: List[str]
    peak_hours: List[Dict]  # {hour: count}

class AnalyticsEngine:
    """Advanced analytics engine for Aetherstore platform"""
    
    def __init__(self):
        self.events_db = []  # Temporary buffer before DB sync
        self.user_metrics_cache = {}
        self.product_metrics_cache = {}
        self.store_metrics_cache = {}
        self.is_calculated = False
        
        logger.info("Analytics Engine initialized")
    
    def add_event(self, event_data: EventData):
        """Add an event to the analytics database and persist to DB"""
        self.events_db.append(event_data)
        self.is_calculated = False

        # Persist specific events to PostgreSQL
        try:
            db = SessionLocal()
            if event_data.event_type == EventType.PURCHASE:
                # Update Store and Product Analytics tables
                self._update_db_metrics(db, event_data)
            elif event_data.event_type == EventType.TRY_ON:
                self._update_tryon_db(db, event_data)
            db.close()
        except Exception as e:
            logger.error(f"Failed to persist event to DB: {e}")

        logger.info(f"Added event: {event_data.event_type.value} for user {event_data.user_id}")

    def _update_db_metrics(self, db: Session, event: EventData):
        """Update persistent database tables for business metrics"""
        date_today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # Update Store Analytics
        store_stat = db.query(StoreAnalytics).filter(
            StoreAnalytics.store_id == event.store_id,
            StoreAnalytics.date == date_today
        ).first()

        if not store_stat:
            store_stat = StoreAnalytics(store_id=event.store_id, date=date_today)
            db.add(store_stat)

        store_stat.purchase_count += 1
        # Revenue update would happen here with real transaction data

        # Update Product Analytics
        if event.product_id:
            prod_stat = db.query(ProductAnalytics).filter(
                ProductAnalytics.product_id == event.product_id,
                ProductAnalytics.date == date_today
            ).first()

            if not prod_stat:
                prod_stat = ProductAnalytics(product_id=event.product_id, date=date_today)
                db.add(prod_stat)
            prod_stat.purchase_count += 1

        db.commit()

    def _update_tryon_db(self, db: Session, event: EventData):
        """Update try-on counters in DB"""
        date_today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # Update Store try-on count
        store_stat = db.query(StoreAnalytics).filter(
            StoreAnalytics.store_id == event.store_id,
            StoreAnalytics.date == date_today
        ).first()
        if store_stat:
            store_stat.tryon_sessions_count += 1

        # Update Product try-on count
        if event.product_id:
            prod_stat = db.query(ProductAnalytics).filter(
                ProductAnalytics.product_id == event.product_id,
                ProductAnalytics.date == date_today
            ).first()
            if prod_stat:
                prod_stat.tryon_count += 1

        db.commit()
    
    def add_events_batch(self, events: List[EventData]):
        """Add multiple events at once"""
        self.events_db.extend(events)
        self.is_calculated = False
        logger.info(f"Added {len(events)} events to analytics database")
    
    def calculate_all_metrics(self):
        """Calculate all metrics - should be called periodically"""
        if not self.events_db or self.is_calculated:
            return
        
        logger.info("Calculating analytics metrics...")
        
        # Calculate all metrics
        self.calculate_user_metrics()
        self.calculate_product_metrics()
        self.calculate_store_metrics()
        
        self.is_calculated = True
        logger.info("Analytics metrics calculated successfully")
    
    def calculate_user_metrics(self):
        """Calculate user behavior metrics"""
        # Group events by user
        user_events = defaultdict(list)
        for event in self.events_db:
            user_events[event.user_id].append(event)
        
        for user_id, events in user_events.items():
            # Calculate metrics for this user
            total_sessions = len(set([e.session_id for e in events]))
            
            # Calculate session durations (simplified)
            session_durations = []
            for session_id in set([e.session_id for e in events]):
                session_events = [e for e in events if e.session_id == session_id]
                if len(session_events) > 1:
                    start_time = min([e.timestamp for e in session_events])
                    end_time = max([e.timestamp for e in session_events])
                    duration = (end_time - start_time).total_seconds() / 60  # in minutes
                    session_durations.append(duration)
            
            avg_session_duration = np.mean(session_durations) if session_durations else 0
            
            # Count different event types
            page_views = len([e for e in events if e.event_type == EventType.PAGE_VIEW])
            products_viewed = len([e for e in events if e.event_type == EventType.PRODUCT_VIEW])
            try_on_count = len([e for e in events if e.event_type == EventType.TRY_ON])
            add_to_cart_count = len([e for e in events if e.event_type == EventType.ADD_TO_CART])
            purchase_count = len([e for e in events if e.event_type == EventType.PURCHASE])
            
            # Conversion rate calculation
            conversion_rate = (purchase_count / try_on_count * 100) if try_on_count > 0 else 0
            
            # Average order value would require purchase amount data
            avg_order_value = 0  # Placeholder - would need transaction data
            
            # Create metrics object
            metrics = UserBehaviorMetrics(
                total_sessions=total_sessions,
                avg_session_duration=avg_session_duration,
                page_views=page_views,
                products_viewed=products_viewed,
                try_on_count=try_on_count,
                add_to_cart_count=add_to_cart_count,
                purchase_count=purchase_count,
                conversion_rate=conversion_rate,
                avg_order_value=avg_order_value,
                last_active=max([e.timestamp for e in events])
            )
            
            self.user_metrics_cache[user_id] = metrics
    
    def calculate_product_metrics(self):
        """Calculate product performance metrics"""
        # Group events by product
        product_events = defaultdict(list)
        for event in self.events_db:
            if event.product_id:
                product_events[event.product_id].append(event)
        
        for product_id, events in product_events.items():
            views = len([e for e in events if e.event_type == EventType.PRODUCT_VIEW])
            try_ons = len([e for e in events if e.event_type == EventType.TRY_ON])
            add_to_cart = len([e for e in events if e.event_type == EventType.ADD_TO_CART])
            purchases = len([e for e in events if e.event_type == EventType.PURCHASE])
            
            # Conversion rates
            view_to_try_on = (try_ons / views * 100) if views > 0 else 0
            try_on_to_purchase = (purchases / try_ons * 100) if try_ons > 0 else 0
            conversion_rate = (purchases / views * 100) if views > 0 else 0
            
            # Placeholder values for avg_rating and revenue
            avg_rating = 4.2  # Would come from actual reviews
            revenue = purchases * 50.0  # Placeholder average price
            
            # Popularity score based on engagement
            popularity_score = (views * 0.1) + (try_ons * 0.3) + (add_to_cart * 0.4) + (purchases * 0.2)
            
            # Determine trend
            recent_events = [e for e in events if e.timestamp > datetime.now() - timedelta(days=7)]
            recent_purchases = len([e for e in recent_events if e.event_type == EventType.PURCHASE])
            previous_events = [e for e in events if e.timestamp <= datetime.now() - timedelta(days=7)]
            previous_purchases = len([e for e in previous_events if e.event_type == EventType.PURCHASE])
            
            if recent_purchases > previous_purchases * 1.2:
                trend = "up"
            elif recent_purchases < previous_purchases * 0.8:
                trend = "down"
            else:
                trend = "stable"
            
            # Create metrics object
            metrics = ProductPerformanceMetrics(
                views=views,
                try_ons=try_ons,
                add_to_cart=add_to_cart,
                purchases=purchases,
                conversion_rate=conversion_rate,
                avg_rating=avg_rating,
                revenue=revenue,
                popularity_score=popularity_score,
                trend=trend
            )
            
            self.product_metrics_cache[product_id] = metrics
    
    def calculate_store_metrics(self):
        """Calculate store performance metrics"""
        # Group events by store
        store_events = defaultdict(list)
        for event in self.events_db:
            store_events[event.store_id].append(event)
        
        for store_id, events in store_events.items():
            total_visitors = len(set([e.user_id for e in events]))
            
            # Calculate average time spent
            session_durations = []
            for session_id in set([e.session_id for e in events]):
                session_events = [e for e in events if e.session_id == session_id]
                if len(session_events) > 1:
                    start_time = min([e.timestamp for e in session_events])
                    end_time = max([e.timestamp for e in session_events])
                    duration = (end_time - start_time).total_seconds() / 60  # in minutes
                    session_durations.append(duration)
            
            avg_time_spent = np.mean(session_durations) if session_durations else 0
            
            # Bounce rate (users who only viewed one page)
            single_page_sessions = 0
            total_sessions = len(set([e.session_id for e in events]))
            for session_id in set([e.session_id for e in events]):
                session_events = [e for e in events if e.session_id == session_id]
                page_views = len([e for e in session_events if e.event_type == EventType.PAGE_VIEW])
                if page_views <= 1:
                    single_page_sessions += 1
            
            bounce_rate = (single_page_sessions / total_sessions * 100) if total_sessions > 0 else 0
            
            # Conversion rate
            purchase_events = [e for e in events if e.event_type == EventType.PURCHASE]
            conversion_rate = (len(purchase_events) / total_visitors * 100) if total_visitors > 0 else 0
            
            # Total revenue (placeholder)
            total_revenue = len(purchase_events) * 75.0  # Average order value
            
            # Cart abandonment rate
            add_to_cart_events = [e for e in events if e.event_type == EventType.ADD_TO_CART]
            cart_abandonment_rate = (
                (len(add_to_cart_events) - len(purchase_events)) / len(add_to_cart_events) * 100
                if add_to_cart_events else 0
            )
            
            # Popular products in this store
            product_purchases = defaultdict(int)
            for event in purchase_events:
                product_purchases[event.product_id] += 1
            popular_products = sorted(product_purchases.items(), key=lambda x: x[1], reverse=True)[:5]
            popular_products = [item[0] for item in popular_products]  # Just the product IDs
            
            # Peak hours
            hour_counts = defaultdict(int)
            for event in events:
                hour_counts[event.timestamp.hour] += 1
            peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            peak_hours = [{"hour": hour, "count": count} for hour, count in peak_hours]
            
            # Create metrics object
            metrics = StorePerformanceMetrics(
                total_visitors=total_visitors,
                avg_time_spent=avg_time_spent,
                bounce_rate=bounce_rate,
                conversion_rate=conversion_rate,
                total_revenue=total_revenue,
                cart_abandonment_rate=cart_abandonment_rate,
                popular_products=popular_products,
                peak_hours=peak_hours
            )
            
            self.store_metrics_cache[store_id] = metrics
    
    def get_user_metrics(self, user_id: str) -> Optional[UserBehaviorMetrics]:
        """Get metrics for a specific user"""
        self.calculate_all_metrics()  # Ensure metrics are current
        return self.user_metrics_cache.get(user_id)
    
    def get_product_metrics(self, product_id: str) -> Optional[ProductPerformanceMetrics]:
        """Get metrics for a specific product"""
        self.calculate_all_metrics()  # Ensure metrics are current
        return self.product_metrics_cache.get(product_id)
    
    def get_store_metrics(self, store_id: str) -> Optional[StorePerformanceMetrics]:
        """Get metrics for a specific store"""
        self.calculate_all_metrics()  # Ensure metrics are current
        return self.store_metrics_cache.get(store_id)
    
    def get_platform_overview(self) -> Dict:
        """Get overall platform performance metrics"""
        self.calculate_all_metrics()  # Ensure metrics are current
        
        total_users = len(self.user_metrics_cache)
        total_products = len(self.product_metrics_cache)
        total_stores = len(self.store_metrics_cache)
        
        # Calculate platform averages
        avg_conversion_rate = np.mean([
            metrics.conversion_rate for metrics in self.user_metrics_cache.values()
        ]) if self.user_metrics_cache else 0
        
        avg_session_duration = np.mean([
            metrics.avg_session_duration for metrics in self.user_metrics_cache.values()
        ]) if self.user_metrics_cache else 0
        
        total_revenue = sum([
            metrics.total_revenue for metrics in self.store_metrics_cache.values()
        ]) if self.store_metrics_cache else 0
        
        return {
            "platform_kpis": {
                "total_users": total_users,
                "total_products": total_products,
                "total_stores": total_stores,
                "total_events": len(self.events_db),
                "avg_user_conversion_rate": round(avg_conversion_rate, 2),
                "avg_session_duration_minutes": round(avg_session_duration, 2),
                "total_revenue": total_revenue
            },
            "time_period": {
                "start_date": min([e.timestamp for e in self.events_db]).isoformat() if self.events_db else None,
                "end_date": max([e.timestamp for e in self.events_db]).isoformat() if self.events_db else None,
                "data_points": len(self.events_db)
            }
        }
    
    def get_top_performing_products(self, limit: int = 10) -> List[Dict]:
        """Get top performing products based on various metrics"""
        self.calculate_all_metrics()
        
        # Sort products by multiple criteria
        sorted_products = sorted(
            self.product_metrics_cache.items(),
            key=lambda x: (x[1].popularity_score, x[1].conversion_rate, x[1].revenue),
            reverse=True
        )
        
        top_products = []
        for product_id, metrics in sorted_products[:limit]:
            top_products.append({
                "product_id": product_id,
                "views": metrics.views,
                "try_ons": metrics.try_ons,
                "purchases": metrics.purchases,
                "conversion_rate": round(metrics.conversion_rate, 2),
                "revenue": round(metrics.revenue, 2),
                "popularity_score": round(metrics.popularity_score, 2),
                "trend": metrics.trend
            })
        
        return top_products
    
    def get_user_engagement_trends(self, days: int = 30) -> Dict:
        """Get user engagement trends over time"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Group events by date
        date_events = defaultdict(list)
        for event in self.events_db:
            if start_date <= event.timestamp <= end_date:
                date_key = event.timestamp.date()
                date_events[date_key].append(event)
        
        trends = {
            "dates": [],
            "new_users": [],
            "active_users": [],
            "total_sessions": [],
            "purchases": [],
            "try_ons": []
        }
        
        for date in sorted(date_events.keys()):
            events = date_events[date]
            trends["dates"].append(date.isoformat())
            trends["new_users"].append(len(set([e.user_id for e in events])))
            trends["active_users"].append(len(set([e.user_id for e in events if e.event_type != EventType.PAGE_VIEW])))
            trends["total_sessions"].append(len(set([e.session_id for e in events])))
            
            purchases = len([e for e in events if e.event_type == EventType.PURCHASE])
            trends["purchases"].append(purchases)
            
            try_ons = len([e for e in events if e.event_type == EventType.TRY_ON])
            trends["try_ons"].append(try_ons)
        
        return trends
    
    def get_heatmap_data(self, store_id: str) -> Dict:
        """Get heatmap data for store analytics including spatial 3D points"""
        store_events = [e for e in self.events_db if e.store_id == store_id]
        
        # Spatial 3D clicks
        spatial_points = []
        for e in store_events:
            if e.event_type == EventType.PRODUCT_VIEW and e.additional_data:
                coords = e.additional_data.get("coords_3d")
                if coords:
                    spatial_points.append(coords)

        # By hour of day
        hour_activity = defaultdict(int)
        for event in store_events:
            hour_activity[event.timestamp.hour] += 1
        
        # By day of week
        day_activity = defaultdict(int)
        for event in store_events:
            day_activity[event.timestamp.weekday()] += 1  # 0=Monday, 6=Sunday
        
        # By product interaction
        product_interactions = defaultdict(int)
        for event in store_events:
            if event.product_id:
                product_interactions[event.product_id] += 1
        
        return {
            "hourly_activity": dict(hour_activity),
            "daily_activity": dict(day_activity),
            "product_interactions": dict(product_interactions),
            "spatial_heatmap_3d": spatial_points,
            "total_interactions": len(store_events)
        }

    def get_conversion_funnel(self, store_id: str = None, product_id: str = None) -> Dict:
        """Calculate the conversion funnel using UserActivity data from DB"""
        db = SessionLocal()
        try:
            from models import UserActivity
            query = db.query(UserActivity)
            if store_id:
                query = query.filter(UserActivity.store_id == store_id)
            if product_id:
                query = query.filter(UserActivity.product_id == product_id)

            activities = query.all()

            counts = {
                "visit_store": 0,
                "view_product": 0,
                "try_on": 0,
                "add_to_cart": 0,
                "purchase": 0
            }

            for a in activities:
                if a.activity_type in counts:
                    counts[a.activity_type] += 1

            # Calculate drops
            funnel = []
            steps = ["visit_store", "view_product", "try_on", "add_to_cart", "purchase"]
            prev_val = None

            for step in steps:
                val = counts[step]
                pct_of_total = (val / counts[steps[0]] * 100) if counts[steps[0]] > 0 else 0
                pct_of_prev = (val / prev_val * 100) if prev_val and prev_val > 0 else 100

                funnel.append({
                    "step": step,
                    "count": val,
                    "percentage_of_total": round(pct_of_total, 2),
                    "percentage_of_previous": round(pct_of_prev, 2)
                })
                prev_val = val

            return {
                "store_id": store_id,
                "product_id": product_id,
                "funnel": funnel,
                "total_conversions": counts["purchase"]
            }
        finally:
            db.close()

# Example usage and testing
class AnalyticsService:
    """Main service class that manages the analytics engine"""
    
    def __init__(self):
        self.analytics_engine = AnalyticsEngine()
        self.is_running = False
        
        logger.info("Analytics Service initialized")
    
    async def start_monitoring(self):
        """Start monitoring and periodically calculating metrics"""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("Analytics monitoring started")
        
        # In a real implementation, this would run continuously
        # For now, just ensure initial calculations are done
        self.analytics_engine.calculate_all_metrics()
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        self.is_running = False
        logger.info("Analytics monitoring stopped")
    
    def track_event(self, event_data: EventData):
        """Track a new event"""
        self.analytics_engine.add_event(event_data)
    
    def track_events_batch(self, events: List[EventData]):
        """Track multiple events at once"""
        self.analytics_engine.add_events_batch(events)
    
    async def get_insights(self, insight_type: str, **kwargs) -> Dict:
        """Get specific insights based on type"""
        if insight_type == "platform_overview":
            return self.analytics_engine.get_platform_overview()
        elif insight_type == "top_products":
            limit = kwargs.get("limit", 10)
            return self.analytics_engine.get_top_performing_products(limit)
        elif insight_type == "user_trends":
            days = kwargs.get("days", 30)
            return self.analytics_engine.get_user_engagement_trends(days)
        elif insight_type == "heatmap":
            store_id = kwargs.get("store_id")
            if store_id:
                return self.analytics_engine.get_heatmap_data(store_id)
        elif insight_type == "user_metrics":
            user_id = kwargs.get("user_id")
            metrics = self.analytics_engine.get_user_metrics(user_id)
            return metrics.__dict__ if metrics else {}
        elif insight_type == "product_metrics":
            product_id = kwargs.get("product_id")
            metrics = self.analytics_engine.get_product_metrics(product_id)
            return metrics.__dict__ if metrics else {}
        elif insight_type == "store_metrics":
            store_id = kwargs.get("store_id")
            metrics = self.analytics_engine.get_store_metrics(store_id)
            return metrics.__dict__ if metrics else {}
        
        return {}

# Example usage
async def main():
    """Example usage of the Analytics Service"""
    service = AnalyticsService()
    
    # Start monitoring
    await service.start_monitoring()
    
    # Simulate tracking some events
    from datetime import datetime
    import random
    
    sample_events = [
        EventData(
            event_type=EventType.PRODUCT_VIEW,
            user_id=f"user_{random.randint(1, 5)}",
            product_id=f"prod_{random.randint(1, 10)}",
            timestamp=datetime.now(),
            session_id=f"session_{random.randint(1, 100)}",
            store_id="store_1"
        )
        for _ in range(100)
    ]
    
    service.track_events_batch(sample_events)
    
    # Get various insights
    print("Platform Overview:")
    overview = await service.get_insights("platform_overview")
    print(json.dumps(overview, indent=2, default=str))
    
    print("\nTop Performing Products:")
    top_products = await service.get_insights("top_products", limit=5)
    for product in top_products:
        print(f"  {product['product_id']}: {product['purchases']} purchases, ${product['revenue']:.2f} revenue")
    
    print("\nUser Engagement Trends (last 7 days):")
    trends = await service.get_insights("user_trends", days=7)
    print(f"  Dates: {len(trends['dates'])}")
    print(f"  Total purchases: {sum(trends['purchases'])}")
    print(f"  Total try-ons: {sum(trends['try_ons'])}")
    
    await service.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(main())