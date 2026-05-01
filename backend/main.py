from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
from pydantic import BaseModel
from typing import Optional, List
import os
from datetime import datetime
import uuid
import asyncio
from ai_processing import AdvancedAIService, BodyMeasurements, ProductFitAnalysis
from recommendation_engine import HybridRecommendationEngine
from analytics_engine import AnalyticsService, EventData, EventType
from vr_integration import VRService
from blockchain_integration import DigitalOwnershipService
from social_integration import SocialShoppingService
from ai_consultant import AIConsultantService
from api.physics import router as physics_router

# Initialize FastAPI app
app = FastAPI(
    title="Aetherstore Engine API",
    description="The ultimate 3D fashion platform API",
    version="1.0.0"
)

# Initialize AI Services
ai_service = AdvancedAIService()
recommendation_engine = HybridRecommendationEngine()
analytics_service = AnalyticsService()
vr_service = VRService()
ownership_service = DigitalOwnershipService()
social_service = SocialShoppingService()
ai_consultant_service = AIConsultantService()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# Pydantic models
class Product(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    price: float
    brand_id: str
    category: str
    size_chart: dict
    material: str
    colors: List[str]
    dimensions: dict  # width, height, depth
    asset_urls: dict  # 3d_model, images
    created_at: Optional[datetime] = None

class Store(BaseModel):
    id: Optional[str] = None
    name: str
    brand_id: str
    description: str
    template: str  # modern-gallery, vintage-loft, luxury-palace, etc.
    products: List[str]  # List of product IDs
    settings: dict  # layout, lighting, music, etc.
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True

class UserAvatar(BaseModel):
    id: Optional[str] = None
    user_id: str
    scan_data_url: str
    measurements: dict  # height, weight, waist, chest, etc.
    body_type: str  # pear, apple, hourglass, etc.
    created_at: Optional[datetime] = None

class TryOnSession(BaseModel):
    id: Optional[str] = None
    user_id: str
    store_id: str
    product_id: str
    avatar_id: str
    tryon_data: dict  # pose, lighting, angle, etc.
    created_at: Optional[datetime] = None

# In-memory storage for development (replace with database in production)
stores_db = []
products_db = []
avatars_db = []
tryon_sessions_db = []

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <head>
            <title>Aetherstore Engine</title>
        </head>
        <body>
            <h1>Welcome to Aetherstore Engine</h1>
            <p>The ultimate 3D fashion platform</p>
            <p>API documentation available at <a href="/docs">/docs</a></p>
            <p>Frontend available at <a href="/static">/static</a></p>
        </body>
    </html>
    """

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/api/stores", response_model=List[Store])
async def get_stores():
    return stores_db

@app.post("/api/stores", response_model=Store)
async def create_store(store: Store):
    store.id = str(uuid.uuid4())
    store.created_at = datetime.now()
    store.updated_at = datetime.now()
    stores_db.append(store)
    return store

@app.get("/api/stores/{store_id}", response_model=Store)
async def get_store(store_id: str):
    for store in stores_db:
        if store.id == store_id:
            return store
    raise HTTPException(status_code=404, detail="Store not found")

@app.put("/api/stores/{store_id}", response_model=Store)
async def update_store(store_id: str, store: Store):
    for i, s in enumerate(stores_db):
        if s.id == store_id:
            store.id = store_id
            store.updated_at = datetime.now()
            stores_db[i] = store
            return store
    raise HTTPException(status_code=404, detail="Store not found")

@app.delete("/api/stores/{store_id}")
async def delete_store(store_id: str):
    for i, store in enumerate(stores_db):
        if store.id == store_id:
            del stores_db[i]
            return {"message": "Store deleted successfully"}
    raise HTTPException(status_code=404, detail="Store not found")

@app.get("/api/products", response_model=List[Product])
async def get_products():
    return products_db

@app.post("/api/products", response_model=Product)
async def create_product(product: Product):
    product.id = str(uuid.uuid4())
    product.created_at = datetime.now()
    products_db.append(product)
    return product

@app.get("/api/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    for product in products_db:
        if product.id == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")

@app.post("/api/upload/3d-model", status_code=201)
async def upload_3d_model(file: UploadFile = File(...)):
    # Validate file type
    if not file.content_type.startswith('model/'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only 3D models accepted.")
    
    # Save file to a temporary location
    file_location = f"backend/uploads/{file.filename}"
    os.makedirs("backend/uploads", exist_ok=True)
    
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "location": file_location
    }

@app.post("/api/upload/avatar", status_code=201)
async def upload_avatar_scan(file: UploadFile = File(...)):
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only images accepted.")
    
    # Save file to a temporary location
    file_location = f"backend/uploads/avatars/{file.filename}"
    os.makedirs("backend/uploads/avatars", exist_ok=True)
    
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "location": file_location
    }

@app.get("/api/avatars/{user_id}", response_model=UserAvatar)
async def get_user_avatar(user_id: str):
    for avatar in avatars_db:
        if avatar.user_id == user_id:
            return avatar
    raise HTTPException(status_code=404, detail="Avatar not found")

@app.post("/api/avatars", response_model=UserAvatar)
async def create_user_avatar(avatar: UserAvatar):
    avatar.id = str(uuid.uuid4())
    avatar.created_at = datetime.now()
    avatars_db.append(avatar)
    return avatar

@app.post("/api/tryon", response_model=TryOnSession)
async def create_tryon_session(session: TryOnSession):
    session.id = str(uuid.uuid4())
    session.created_at = datetime.now()
    tryon_sessions_db.append(session)
    return session

@app.get("/api/tryon/{session_id}", response_model=TryOnSession)
async def get_tryon_session(session_id: str):
    for session in tryon_sessions_db:
        if session.id == session_id:
            return session
    raise HTTPException(status_code=404, detail="Try-on session not found")

# AI Processing Endpoints
@app.post("/api/ai/process-avatar")
async def process_avatar(file: UploadFile = File(...)):
    """Process an avatar scan using AI to extract measurements"""
    try:
        # Save uploaded file temporarily
        temp_path = f"backend/temp/{file.filename}"
        os.makedirs("backend/temp", exist_ok=True)
        
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # Process with AI service
        result = await ai_service.process_avatar_scan(temp_path)
        
        # Clean up temp file
        os.remove(temp_path)
        
        if result:
            return JSONResponse(content=result, status_code=200)
        else:
            raise HTTPException(status_code=400, detail="Could not process avatar scan")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing avatar: {str(e)}")

@app.post("/api/ai/analyze-fit")
async def analyze_product_fit():
    """Analyze how well a product fits a user (placeholder - would need avatar path and product details)"""
    # This would typically receive avatar data and product info
    # For now, returning a sample response
    sample_analysis = {
        "recommended_size": "M",
        "confidence": 0.85,
        "fit_score": 0.92,
        "measurement_differences": {
            "chest": 2.0,
            "waist": 1.5,
            "hips": 0.5
        },
        "size_chart": {
            "S": {"chest": 85, "waist": 65, "hips": 90},
            "M": {"chest": 90, "waist": 70, "hips": 95},
            "L": {"chest": 95, "waist": 75, "hips": 100}
        },
        "body_type": "hourglass",
        "style_compatibility": 0.88
    }
    return JSONResponse(content=sample_analysis, status_code=200)

@app.post("/api/ai/generate-3d-model")
async def generate_3d_model(file: UploadFile = File(...)):
    """Generate a 3D model from a product image"""
    try:
        # Save uploaded file temporarily
        temp_path = f"backend/temp/{file.filename}"
        os.makedirs("backend/temp", exist_ok=True)
        
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # Process with AI service
        result = await ai_service.generate_3d_product_model(temp_path)
        
        # Clean up temp file
        os.remove(temp_path)
        
        if result:
            return JSONResponse(content=result, status_code=200)
        else:
            raise HTTPException(status_code=400, detail="Could not generate 3D model")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating 3D model: {str(e)}")

@app.get("/api/ai/style-recommendations/{user_id}")
async def get_style_recommendations(user_id: str):
    """Get AI-powered style recommendations for a user"""
    # This would access user's avatar and preferences
    # For now, returning sample recommendations
    recommendations = {
        "user_id": user_id,
        "recommendations": [
            {
                "category": "tops",
                "style": "A-line skirts to balance proportions",
                "confidence": 0.92,
                "reason": "Based on pear body type"
            },
            {
                "category": "bottoms",
                "style": "Statement tops to draw attention upward",
                "confidence": 0.88,
                "reason": "Complements your body shape"
            },
            {
                "category": "outerwear",
                "style": "Structured jackets to balance hips",
                "confidence": 0.85,
                "reason": "Creates visual balance"
            }
        ],
        "body_type_analysis": "pear",
        "last_updated": datetime.now().isoformat()
    }
    return JSONResponse(content=recommendations, status_code=200)

@app.post("/api/ai/fit-prediction")
async def predict_fit(product_data: dict):
    """Predict how well a product will fit based on user measurements"""
    # This would typically be called with product details and user avatar data
    # For now, returning a sample prediction
    fit_prediction = {
        "product_id": product_data.get("product_id", "unknown"),
        "predicted_sizes": {
            "XS": 0.3,
            "S": 0.7,
            "M": 0.95,
            "L": 0.6,
            "XL": 0.2
        },
        "recommended_size": "M",
        "confidence": 0.95,
        "fit_description": "Perfect fit expected",
        "alteration_recommendations": ["None needed"]
    }
    return JSONResponse(content=fit_prediction, status_code=200)

# Recommendation Engine Endpoints
@app.post("/api/recommendations/train")
async def train_recommendation_engine():
    """Train the recommendation engine with current data"""
    try:
        # In a real implementation, this would fetch current user, product, and interaction data
        # For now, using sample data
        interactions = [
            {"user_id": "user1", "product_id": "prod1", "interaction_type": "view", "timestamp": "2023-01-01"},
            {"user_id": "user1", "product_id": "prod2", "interaction_type": "try-on", "timestamp": "2023-01-02"},
            {"user_id": "user1", "product_id": "prod3", "interaction_type": "purchase", "timestamp": "2023-01-03"},
            {"user_id": "user2", "product_id": "prod1", "interaction_type": "view", "timestamp": "2023-01-01"},
            {"user_id": "user2", "product_id": "prod3", "interaction_type": "try-on", "timestamp": "2023-01-02"},
            {"user_id": "user3", "product_id": "prod2", "interaction_type": "purchase", "timestamp": "2023-01-01"},
        ]
        
        users = [
            {"id": "user1", "preferred_colors": "blue,black", "preferred_brands": "brand1,brand2", "style_preferences": "casual,elegant"},
            {"id": "user2", "preferred_colors": "red,white", "preferred_brands": "brand2,brand3", "style_preferences": "trendy,sporty"},
            {"id": "user3", "preferred_colors": "black,gray", "preferred_brands": "brand1,brand3", "style_preferences": "classic,professional"},
        ]
        
        products_list = []
        for product in products_db:  # Assuming products_db is available
            products_list.append({
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "category": product.category,
                "brand": "default_brand",  # Would come from actual product data
                "attributes": {
                    "color": "multicolor",
                    "material": "cotton",
                    "style": "fashion"
                }
            })
        
        # Train the recommendation engine
        await recommendation_engine.train(interactions, users, products_list)
        
        return JSONResponse(content={"message": "Recommendation engine trained successfully", "status": "success"}, status_code=200)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error training recommendation engine: {str(e)}")

@app.get("/api/recommendations/{user_id}")
async def get_user_recommendations(user_id: str, n_recommendations: int = 10):
    """Get personalized recommendations for a user"""
    try:
        # Get recommendations from the trained engine
        recommendations = await recommendation_engine.get_recommendations(user_id, n_recommendations)
        
        # Format recommendations for response
        formatted_recs = []
        for rec in recommendations:
            formatted_recs.append({
                "product_id": rec.product_id,
                "score": rec.score,
                "reason": rec.reason,
                "category": rec.category,
                "brand_affinity": rec.brand_affinity,
                "style_compatibility": rec.style_compatibility
            })
        
        return JSONResponse(content={"user_id": user_id, "recommendations": formatted_recs}, status_code=200)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}")

@app.get("/api/recommendations/similar/{product_id}")
async def get_similar_products(product_id: str, n_products: int = 5):
    """Get products similar to a given product"""
    try:
        # Get similar items from the recommendation engine
        similar_items = await recommendation_engine.get_similar_items(product_id, n_products)
        
        # Format similar items for response
        formatted_items = []
        for item in similar_items:
            formatted_items.append({
                "product_id": item.product_id,
                "score": item.score,
                "reason": item.reason,
                "category": item.category
            })
        
        return JSONResponse(content={"product_id": product_id, "similar_products": formatted_items}, status_code=200)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting similar products: {str(e)}")

@app.post("/api/recommendations/feedback/{user_id}/{product_id}")
async def record_recommendation_feedback(user_id: str, product_id: str, feedback_data: dict):
    """Record feedback on a recommendation to improve future suggestions"""
    try:
        # In a real implementation, this would update the user's profile and retrain models
        feedback_type = feedback_data.get('feedback_type', 'neutral')  # positive, negative, neutral
        rating = feedback_data.get('rating', 0)  # 1-5 star rating
        
        # Update user model with feedback
        new_interaction = [{
            'user_id': user_id,
            'product_id': product_id,
            'interaction_type': 'feedback',
            'feedback_type': feedback_type,
            'rating': rating,
            'timestamp': datetime.now().isoformat()
        }]
        
        await recommendation_engine.retrain_user_model(user_id, new_interaction)
        
        return JSONResponse(content={"message": "Feedback recorded successfully", "user_id": user_id, "product_id": product_id}, status_code=200)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording feedback: {str(e)}")

# Analytics Engine Endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize analytics service on startup"""
    await analytics_service.start_monitoring()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up analytics service on shutdown"""
    await analytics_service.stop_monitoring()

@app.post("/api/analytics/event")
async def track_user_event(event_data: dict):
    """Track a user event for analytics"""
    try:
        # Validate event data
        required_fields = ['event_type', 'user_id', 'session_id', 'store_id']
        for field in required_fields:
            if field not in event_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Create EventData object
        event_obj = EventData(
            event_type=EventType(event_data['event_type']),
            user_id=event_data['user_id'],
            product_id=event_data.get('product_id', ''),
            timestamp=datetime.fromisoformat(event_data.get('timestamp', datetime.now().isoformat())),
            session_id=event_data['session_id'],
            store_id=event_data['store_id'],
            additional_data=event_data.get('additional_data', {})
        )
        
        # Track the event
        analytics_service.track_event(event_obj)
        
        return JSONResponse(content={"message": "Event tracked successfully", "status": "success"}, status_code=200)
    
    except ValueError as e:
        # This catches invalid EventType values
        raise HTTPException(status_code=400, detail=f"Invalid event type: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking event: {str(e)}")

@app.get("/api/analytics/platform-overview")
async def get_platform_overview():
    """Get overall platform performance metrics"""
    try:
        insights = await analytics_service.get_insights("platform_overview")
        return JSONResponse(content=insights, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting platform overview: {str(e)}")

@app.get("/api/analytics/top-products")
async def get_top_products(limit: int = 10):
    """Get top performing products"""
    try:
        insights = await analytics_service.get_insights("top_products", limit=limit)
        return JSONResponse(content={"top_products": insights}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting top products: {str(e)}")

@app.get("/api/analytics/user-trends")
async def get_user_trends(days: int = 30):
    """Get user engagement trends"""
    try:
        insights = await analytics_service.get_insights("user_trends", days=days)
        return JSONResponse(content=insights, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user trends: {str(e)}")

@app.get("/api/analytics/user-metrics/{user_id}")
async def get_user_metrics(user_id: str):
    """Get metrics for a specific user"""
    try:
        insights = await analytics_service.get_insights("user_metrics", user_id=user_id)
        return JSONResponse(content=insights, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user metrics: {str(e)}")

@app.get("/api/analytics/product-metrics/{product_id}")
async def get_product_metrics(product_id: str):
    """Get metrics for a specific product"""
    try:
        insights = await analytics_service.get_insights("product_metrics", product_id=product_id)
        return JSONResponse(content=insights, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting product metrics: {str(e)}")

@app.get("/api/analytics/store-metrics/{store_id}")
async def get_store_metrics(store_id: str):
    """Get metrics for a specific store"""
    try:
        insights = await analytics_service.get_insights("store_metrics", store_id=store_id)
        return JSONResponse(content=insights, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting store metrics: {str(e)}")

@app.get("/api/analytics/heatmap/{store_id}")
async def get_store_heatmap(store_id: str):
    """Get heatmap data for store analytics"""
    try:
        insights = await analytics_service.get_insights("heatmap", store_id=store_id)
        return JSONResponse(content=insights, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting store heatmap: {str(e)}")


# VR Integration Endpoints
@app.post("/api/vr/enable/{user_id}/{store_id}")
async def enable_vr_mode(user_id: str, store_id: str):
    """Enable VR mode for a user in a specific store"""
    try:
        result = await vr_service.enable_vr_mode(user_id, store_id)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/vr/session/{session_id}/events")
async def get_vr_events(session_id: str):
    """Get VR session events and interactions"""
    try:
        events = vr_service.process_vr_events(session_id)
        return JSONResponse(content={"session_id": session_id, "events": events}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/vr/disable/{session_id}")
async def disable_vr_mode(session_id: str):
    """Disable VR mode"""
    try:
        success = await vr_service.disable_vr_mode(session_id)
        return JSONResponse(content={"success": success, "session_id": session_id}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Blockchain Integration Endpoints
@app.post("/api/blockchain/create-asset")
async def create_digital_fashion_item(item_data: dict):
    """Create a new digital fashion item on blockchain"""
    try:
        result = await ownership_service.create_digital_fashion_item(
            item_data.get("name"),
            item_data.get("description"),
            item_data.get("creator_id"),
            item_data.get("metadata", {})
        )
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/blockchain/mint-nft/{asset_id}")
async def mint_fashion_nft(asset_id: str, owner_data: dict):
    """Mint an NFT for a digital fashion item"""
    try:
        result = await ownership_service.mint_fashion_nft(asset_id, owner_data.get("owner_address"))
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/blockchain/transfer/{asset_id}")
async def transfer_fashion_item(asset_id: str, transfer_data: dict):
    """Transfer a digital fashion item between users"""
    try:
        result = await ownership_service.transfer_fashion_item(
            asset_id,
            transfer_data.get("from_address"),
            transfer_data.get("to_address")
        )
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/blockchain/verify-ownership/{asset_id}/{owner_address}")
async def verify_ownership(asset_id: str, owner_address: str):
    """Verify if user owns a specific fashion item"""
    try:
        result = await ownership_service.verify_fashion_ownership(asset_id, owner_address)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/blockchain/collection/{user_address}")
async def get_user_collection(user_address: str):
    """Get all digital fashion items owned by a user"""
    try:
        result = await ownership_service.get_user_fashion_collection(user_address)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Social Shopping Integration Endpoints
@app.post("/api/social/add-friend/{user_id}/{friend_id}")
async def add_friend_endpoint(user_id: str, friend_id: str):
    """Add a friend to user's network"""
    try:
        result = await social_service.add_friend(user_id, friend_id)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/social/friends/{user_id}")
async def get_friends_list(user_id: str):
    """Get user's friend list"""
    try:
        result = await social_service.get_friends_list(user_id)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/social/group-shopping/create")
async def create_group_shopping_session(group_data: dict):
    """Create a new group shopping session"""
    try:
        result = await social_service.create_group_shopping_session(
            group_data.get("name"),
            group_data.get("creator_id"),
            group_data.get("members", []),
            group_data.get("store_id")
        )
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/social/group-shopping/start/{session_id}")
async def start_group_session_endpoint(session_id: str):
    """Start a group shopping session"""
    try:
        result = await social_service.start_group_session(session_id)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/social/style-recommendation")
async def add_style_recommendation_endpoint(recommendation_data: dict):
    """Add a style recommendation from one user to another"""
    try:
        result = await social_service.add_style_recommendation(
            recommendation_data.get("by_user_id"),
            recommendation_data.get("for_user_id"),
            recommendation_data.get("product_id"),
            recommendation_data.get("reason", ""),
            recommendation_data.get("rating", 3.0)
        )
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/social/share-item/{user_id}")
async def share_item_with_friends_endpoint(user_id: str, share_data: dict):
    """Share an item with friends"""
    try:
        result = await social_service.share_item_with_friends(
            user_id,
            share_data.get("item_id"),
            share_data.get("recipients", [])
        )
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/social/activity/{user_id}")
async def get_user_social_activity(user_id: str):
    """Get user's social activity"""
    try:
        result = await social_service.get_user_social_activity(user_id)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/social/live-shopping/join/{room_id}/{user_id}")
async def join_live_shopping_session(room_id: str, user_id: str):
    """Join a live shopping session"""
    try:
        result = await social_service.join_live_shopping_session(room_id, user_id)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/social/group-message/{room_id}/{user_id}")
async def send_group_message_endpoint(room_id: str, user_id: str, message_data: dict):
    """Send a message in a group session"""
    try:
        result = await social_service.send_group_message(room_id, user_id, message_data.get("message"))
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/social/group-messages/{room_id}")
async def get_group_messages(room_id: str, limit: int = 10):
    """Get messages from a group session"""
    try:
        result = await social_service.get_group_messages(room_id, limit)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# AI Fashion Consultant Endpoints
@app.post("/api/consultant/create-profile/{user_id}")
async def create_user_style_profile_endpoint(user_id: str, profile_data: dict):
    """Create user's fashion profile"""
    try:
        result = await ai_consultant_service.create_user_style_profile(
            user_id,
            profile_data.get("body_type", "hourglass"),
            profile_data.get("height", 170.0),
            profile_data.get("age", 25),
            profile_data.get("style_preferences", []),
            profile_data.get("color_preferences", []),
            profile_data.get("size_preferences", {}),
            profile_data.get("budget_level", "medium"),
            profile_data.get("lifestyle", "work"),
            profile_data.get("seasonal_preferences", ["fall", "winter"]),
            profile_data.get("fashion_goals", ["professional", "elegant"])
        )
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/consultant/add-wardrobe-item/{user_id}")
async def add_wardrobe_item_endpoint(user_id: str, item_data: dict):
    """Add an item to user's wardrobe"""
    try:
        result = await ai_consultant_service.add_wardrobe_item(
            user_id,
            item_data.get("name"),
            item_data.get("category"),
            item_data.get("color"),
            item_data.get("brand"),
            item_data.get("style_tags", [])
        )
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/consultant/wardrobe-analysis/{user_id}")
async def get_wardrobe_analysis(user_id: str):
    """Get analysis of user's wardrobe"""
    try:
        result = await ai_consultant_service.get_wardrobe_analysis(user_id)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/consultant/outfit-recommendation/{user_id}")
async def get_outfit_recommendation(user_id: str, occasion: str = "casual"):
    """Get personalized outfit recommendation"""
    try:
        result = await ai_consultant_service.get_outfit_recommendation(user_id, occasion)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/consultant/styling-advice/{user_id}")
async def get_styling_advice(user_id: str, body_type: str = "hourglass"):
    """Get personalized styling advice"""
    try:
        result = await ai_consultant_service.get_styling_advice(user_id, body_type)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/consultant/wardrobe-suggestions/{user_id}")
async def get_wardrobe_suggestions(user_id: str):
    """Get suggestions for wardrobe additions"""
    try:
        result = await ai_consultant_service.get_wardrobe_suggestions(user_id)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/consultant/start-session/{user_id}")
async def start_fashion_consultation(user_id: str, consultant_type: str = "style_advisor"):
    """Start a fashion consultation session"""
    try:
        result = await ai_consultant_service.start_fashion_consultation(user_id, consultant_type)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/consultant/trends")
async def get_current_trends(category: str = None):
    """Get current fashion trends"""
    try:
        result = await ai_consultant_service.get_current_trends(category)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


app.include_router(physics_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)