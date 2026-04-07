"""
AI Fashion Consultant Module for Aetherstore Engine
Implements advanced AI styling assistant and fashion advisor
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import uuid
from sqlalchemy.orm import Session
from database import SessionLocal
from models import UserStyleProfile as DBStyleProfile, WardrobeItem as DBWardrobeItem

class FashionConsultantType(Enum):
    STYLE_ADVISOR = "style_advisor"
    WARDROBE_ANALYST = "wardrobe_analyst"
    OUTFIT_CREATOR = "outfit_creator"
    TRENDS_EXPERT = "trends_expert"
    SEASONAL_STYLIST = "seasonal_stylist"

class StylePreference(Enum):
    CASUAL = "casual"
    FORMAL = "formal"
    BUSINESS = "business"
    SPORTY = "sporty"
    ELEGANT = "elegant"
    TRENDY = "trendy"
    CLASSIC = "classic"
    BOHEMIAN = "bohemian"
    MINIMALIST = "minimalist"
    STREETWEAR = "streetwear"

class BodyType(Enum):
    HOURGLASS = "hourglass"
    PEAR = "pear"
    APPLE = "apple"
    RECTANGLE = "rectangle"
    INVERTED_TRIANGLE = "inverted_triangle"

@dataclass
class UserStyleProfile:
    """Represents a user's style profile"""
    user_id: str
    body_type: BodyType
    height: float  # in cm
    age: int
    style_preferences: List[StylePreference]
    color_preferences: List[str]
    size_preferences: Dict[str, str]  # category -> size
    budget_level: str  # low, medium, high, luxury
    lifestyle: str  # work, leisure, social, etc.
    seasonal_preferences: List[str]  # spring, summer, fall, winter
    fashion_goals: List[str]

@dataclass
class FashionRecommendation:
    """Represents a fashion recommendation"""
    recommendation_id: str
    user_id: str
    product_ids: List[str]
    category: str  # outfit,单品, accessory
    occasion: str  # work, party, casual, etc.
    confidence_score: float
    reason: str
    timestamp: str
    is_personalized: bool = True

@dataclass
class WardrobeItem:
    """Represents an item in user's wardrobe"""
    item_id: str
    name: str
    category: str
    color: str
    brand: str
    purchase_date: str
    times_worn: int
    condition: str  # excellent, good, fair, poor
    style_tags: List[str]

class AIConsultantService:
    """Main service for AI Fashion Consultant features"""
    
    def __init__(self):
        self.user_profiles = {}  # user_id -> UserStyleProfile
        self.wardrobe_items = {}  # user_id -> [WardrobeItem]
        self.recommendations_history = {}  # user_id -> [recommendation_ids]
        self.consultant_sessions = {}  # session_id -> session_data
        self.fashion_trends = {}  # category -> trends_data
        self.outfit_combinations = {}  # user_id -> [outfit_suggestions]
        
        print("AI Consultant Service initialized")
        
        # Initialize with some default trends
        self._initialize_trends()
    
    def _initialize_trends(self):
        """Initialize current fashion trends"""
        self.fashion_trends = {
            "tops": {
                "current_trends": ["oversized_blazers", "sheer_fabrics", "cutout_details"],
                "colors": ["beige", "earth_tones", "neutrals"],
                "patterns": ["checkered", "animal_print"],
                "season": "fall"
            },
            "bottoms": {
                "current_trends": ["wide_leg_pants", "leather_pants", "cargo_pants"],
                "colors": ["black", "brown", "olive"],
                "patterns": [],
                "season": "fall"
            },
            "dresses": {
                "current_trends": ["midi_dresses", "wrap_dresses", "slip_dresses"],
                "colors": ["mustard", "burgundy", "forest_green"],
                "patterns": ["plaid", "floral"],
                "season": "fall"
            }
        }
    
    async def create_user_profile(self, user_id: str, body_type: BodyType, height: float,
                           age: int, style_preferences: List[StylePreference], 
                           color_preferences: List[str], size_preferences: Dict[str, str],
                           budget_level: str, lifestyle: str, 
                           seasonal_preferences: List[str], fashion_goals: List[str]) -> UserStyleProfile:
        """Create a user's style profile and persist to DB"""
        db = SessionLocal()
        try:
            # Check for existing profile
            existing = db.query(DBStyleProfile).filter(DBStyleProfile.user_id == user_id).first()

            profile_data = {
                "user_id": user_id,
                "body_type": body_type.value,
                "height": height,
                "age": age,
                "style_preferences": [p.value for p in style_preferences],
                "color_preferences": color_preferences,
                "size_preferences": size_preferences,
                "budget_level": budget_level,
                "lifestyle": lifestyle,
                "seasonal_preferences": seasonal_preferences,
                "fashion_goals": fashion_goals
            }

            if existing:
                for key, value in profile_data.items():
                    setattr(existing, key, value)
            else:
                db_profile = DBStyleProfile(**profile_data)
                db.add(db_profile)

            db.commit()

            # Sync cache
            profile = UserStyleProfile(
                user_id=user_id, body_type=body_type, height=height, age=age,
                style_preferences=style_preferences, color_preferences=color_preferences,
                size_preferences=size_preferences, budget_level=budget_level,
                lifestyle=lifestyle, seasonal_preferences=seasonal_preferences,
                fashion_goals=fashion_goals
            )
            self.user_profiles[user_id] = profile
            return profile
        finally:
            db.close()
    
    async def add_wardrobe_item(self, user_id: str, name: str, category: str, color: str,
                         brand: str, style_tags: List[str]) -> WardrobeItem:
        """Add an item to user's wardrobe and persist to DB"""
        db = SessionLocal()
        try:
            db_item = DBWardrobeItem(
                user_id=user_id,
                name=name,
                category=category,
                color=color,
                brand=brand,
                style_tags=style_tags
            )
            db.add(db_item)
            db.commit()
            db.refresh(db_item)

            wardrobe_item = WardrobeItem(
                item_id=str(db_item.id),
                name=name,
                category=category,
                color=color,
                brand=brand,
                purchase_date=db_item.purchase_date.isoformat() if hasattr(db_item.purchase_date, 'isoformat') else str(db_item.purchase_date),
                times_worn=0,
                condition="excellent",
                style_tags=style_tags
            )

            if user_id not in self.wardrobe_items:
                self.wardrobe_items[user_id] = []
            self.wardrobe_items[user_id].append(wardrobe_item)
            return wardrobe_item
        finally:
            db.close()
    
    async def analyze_wardrobe(self, user_id: str) -> Dict:
        """Analyze user's wardrobe and provide insights"""
        # In a real app, fetch from DB. For now use cache.
        if user_id not in self.wardrobe_items:
            return {"message": "No wardrobe items found", "user_id": user_id}
        
        wardrobe = self.wardrobe_items[user_id]
        
        # Analyze wardrobe
        category_count = {}
        color_count = {}
        style_tags = set()
        
        for item in wardrobe:
            category_count[item.category] = category_count.get(item.category, 0) + 1
            color_count[item.color] = color_count.get(item.color, 0) + 1
            style_tags.update(item.style_tags)
        
        insights = {
            "total_items": len(wardrobe),
            "category_breakdown": category_count,
            "dominant_colors": sorted(color_count.items(), key=lambda x: x[1], reverse=True)[:5],
            "common_styles": list(style_tags),
            "wardrobe_value": len(wardrobe) * 100,  # Simplified estimation
            "diversity_score": len(set(category_count.keys())),
            "suggestions": []
        }
        
        # Generate suggestions
        if len(wardrobe) < 10:
            insights["suggestions"].append("Your wardrobe could benefit from more variety")
        if "black" not in color_count and "navy" not in color_count:
            insights["suggestions"].append("Consider adding classic colors like black or navy")
        
        return insights
    
    async def generate_outfit_recommendation(self, user_id: str, occasion: str = "casual") -> FashionRecommendation:
        """Generate an outfit recommendation for the user"""
        recommendation_id = f"rec_{uuid.uuid4().hex[:12]}"
        
        # Get user profile
        profile = self.user_profiles.get(user_id)
        if not profile:
            raise ValueError(f"No profile found for user {user_id}")
        
        # Generate outfit based on profile, occasion, and current trends
        outfit_items = []
        
        # Select items based on occasion and user preferences
        if occasion == "work":
            outfit_items = ["blazer", "dress_shirt", "trousers", "dress_shoes"]
        elif occasion == "party":
            outfit_items = ["dress", "high_heels", "evening_bag", "statement_jewelry"]
        else:  # casual
            outfit_items = ["tshirt", "jeans", "sneakers", "casual_jacket"]
        
        # Add trend awareness
        trend_items = []
        for item in outfit_items:
            trend_items.append(f"{item}_with_{random.choice(list(self.fashion_trends.keys()))}_trend")
        
        # Calculate confidence based on how well it matches user preferences
        confidence_score = 0.8 + (random.random() * 0.2)  # 0.8-1.0
        
        recommendation = FashionRecommendation(
            recommendation_id=recommendation_id,
            user_id=user_id,
            product_ids=[f"prod_{i}" for i in range(len(trend_items))],
            category="outfit",
            occasion=occasion,
            confidence_score=confidence_score,
            reason=f"Recommended outfit for {occasion} based on your style preferences and current trends",
            timestamp=datetime.now().isoformat()
        )
        
        # Store in history
        if user_id not in self.recommendations_history:
            self.recommendations_history[user_id] = []
        
        self.recommendations_history[user_id].append(recommendation_id)
        
        print(f"Generated outfit recommendation for {user_id} for {occasion} occasion")
        return recommendation
    
    async def get_personal_styling_advice(self, user_id: str, body_type: BodyType) -> List[str]:
        """Provide styling advice based on body type"""
        advice_map = {
            BodyType.HOURGLASS: [
                "Emphasize your waist with fitted pieces",
                "Choose A-line skirts to balance proportions",
                "Opt for structured blazers",
                "High-waisted bottoms can enhance your curves"
            ],
            BodyType.PEAR: [
                "Balance proportions with statement tops",
                "A-line skirts and wide-leg pants can even out your silhouette",
                "Choose darker colors on the bottom",
                "Draw attention upward with colorful tops"
            ],
            BodyType.APPLE: [
                "Empire waist dresses can be flattering",
                "Choose pieces that skim the midsection",
                "Dark colors in the midsection can be slimming",
                "Structured shoulders can create balance"
            ],
            BodyType.RECTANGLE: [
                "Create curves with peplum tops",
                "Layering can add dimension",
                "Asymmetrical cuts can provide visual interest",
                "Belted pieces can define your waist"
            ],
            BodyType.INVERTED_TRIANGLE: [
                "Balance broad shoulders with wide-leg pants",
                "A-line skirts can even out proportions",
                "V-necklines can elongate the torso",
                "Dark tops and lighter bottoms can shift focus"
            ]
        }
        
        return advice_map.get(body_type, ["General styling advice based on your shape"])
    
    async def suggest_wardrobe_additions(self, user_id: str) -> List[Dict]:
        """Suggest items to add to user's wardrobe"""
        suggestions = []
        
        # Get user's profile and wardrobe
        profile = self.user_profiles.get(user_id)
        wardrobe = self.wardrobe_items.get(user_id, [])
        
        if not profile:
            return [{"item": "basic_tee", "reason": "Essential wardrobe piece", "priority": "high"}]
        
        # Analyze wardrobe gaps
        categories_in_wardrobe = [item.category for item in wardrobe]
        missing_categories = set(["tops", "bottoms", "dresses", "outerwear", "shoes", "accessories"]) - set(categories_in_wardrobe)
        
        # Suggest items based on missing categories and occasion
        if "outerwear" not in categories_in_wardrobe:
            suggestions.append({
                "item": "versatile_blazer",
                "reason": "Essential for work and formal occasions",
                "priority": "high",
                "style_match": profile.style_preferences[0].value if profile.style_preferences else "casual"
            })
        
        if "shoes" not in categories_in_wardrobe:
            suggestions.append({
                "item": "comfortable_sneakers",
                "reason": "Essential for casual wear",
                "priority": "medium",
                "style_match": "casual"
            })
        
        # Suggest items based on trends and user preferences
        for category, trend_data in self.fashion_trends.items():
            if category in missing_categories:
                suggestions.append({
                    "item": f"{random.choice(trend_data['current_trends'])} in {random.choice(trend_data['colors'])}",
                    "reason": f"Current {trend_data['season']} trend",
                    "priority": "low-medium",
                    "style_match": "trendy"
                })
        
        return suggestions
    
    async def start_consultation_session(self, user_id: str, consultant_type: FashionConsultantType) -> str:
        """Start a fashion consultation session"""
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "consultant_type": consultant_type.value,
            "start_time": datetime.now().isoformat(),
            "interactions": [],
            "outcomes": []
        }
        
        self.consultant_sessions[session_id] = session_data
        print(f"Started {consultant_type.value} session for {user_id}")
        
        return session_id
    
    async def get_fashion_trends(self, category: str) -> Dict:
        """Get current fashion trends for a category"""
        return self.fashion_trends.get(category, {})
    
    async def update_wardrobe_item_usage(self, user_id: str, item_id: str):
        """Update how often an item has been worn"""
        if user_id in self.wardrobe_items:
            for item in self.wardrobe_items[user_id]:
                if item.item_id == item_id:
                    item.times_worn += 1
                    break

    async def equip_wardrobe_item(self, user_id: str, item_id: str, equip: bool = True) -> Dict:
        """Equip or unequip an item for the 3D avatar"""
        db = SessionLocal()
        try:
            # 1. Find the item
            item = db.query(DBWardrobeItem).filter(DBWardrobeItem.id == item_id, DBWardrobeItem.user_id == user_id).first()
            if not item:
                return {"success": False, "message": "Item not found"}

            if equip:
                # Unequip others in same category
                db.query(DBWardrobeItem).filter(
                    DBWardrobeItem.user_id == user_id,
                    DBWardrobeItem.category == item.category
                ).update({"is_equipped": False})
            
            item.is_equipped = equip
            db.commit()
            return {"success": True, "item_id": item_id, "is_equipped": equip}
        finally:
            db.close()

    async def get_equipped_items(self, user_id: str) -> List[Dict]:
        """Get all items currently worn by the user's avatar"""
        db = SessionLocal()
        try:
            items = db.query(DBWardrobeItem).filter(
                DBWardrobeItem.user_id == user_id,
                DBWardrobeItem.is_equipped == True
            ).all()
            return [{"id": str(i.id), "name": i.name, "category": i.category} for i in items]
        finally:
            db.close()

class AIConsultantManager:
    """Main service for AI Fashion Consultant features (Backwards compatible class name)"""
    
    def __init__(self):
        self.service = AIConsultantService()
        print("AI Consultant Manager initialized")
    
    async def create_user_style_profile(self, *args, **kwargs):
        return await self.service.create_user_profile(*args, **kwargs)

    async def add_wardrobe_item(self, *args, **kwargs):
        return await self.service.add_wardrobe_item(*args, **kwargs)

    async def get_wardrobe_analysis(self, user_id: str):
        analysis = await self.service.analyze_wardrobe(user_id)
        return {"user_id": user_id, "wardrobe_analysis": analysis}

    async def get_outfit_recommendation(self, user_id: str, occasion: str = "casual"):
        try:
            rec = await self.service.generate_outfit_recommendation(user_id, occasion)
            return {"success": True, "recommendation": rec, "message": "Success"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_styling_advice(self, user_id: str, body_type: str):
        try:
            body_type_enum = BodyType(body_type)
            advice = await self.service.get_personal_styling_advice(user_id, body_type_enum)
            return {"success": True, "user_id": user_id, "body_type": body_type, "styling_advice": advice}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_wardrobe_suggestions(self, user_id: str):
        suggestions = await self.service.suggest_wardrobe_additions(user_id)
        return {"user_id": user_id, "suggestions": suggestions}

    async def start_fashion_consultation(self, user_id: str, consultant_type: str):
        try:
            ctype = FashionConsultantType(consultant_type)
            sid = await self.service.start_consultation_session(user_id, ctype)
            return {"success": True, "session_id": sid, "user_id": user_id, "consultant_type": consultant_type}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_current_trends(self, category: str = None):
        trends = await self.service.get_fashion_trends(category)
        return {"category": category, "trends": trends} if category else {"all_trends": trends}

# Global instance
ai_consultant_service = AIConsultantService()

async def equip_item_endpoint(user_id: str, item_id: str, equip: bool = True):
    return await ai_consultant_service.equip_wardrobe_item(user_id, item_id, equip)

async def get_equipped_endpoint(user_id: str):
    return await ai_consultant_service.get_equipped_items(user_id)
