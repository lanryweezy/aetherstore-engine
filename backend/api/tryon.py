# api/tryon.py
# Try-on session management API endpoints for Aetherstore Engine

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from models import TryOnSession as DBTryOnSession, User, Product, Store, UserAvatar
from crud import get_tryon_session, create_tryon_session, update_tryon_session, delete_tryon_session
from crud import get_user, get_product, get_store, get_user_avatar
from auth import get_current_active_user
from database import get_db_session

router = APIRouter()

# Pydantic models for request/response
class TryOnCreate(BaseModel):
    store_id: str
    product_id: str
    avatar_id: Optional[str] = None
    session_data: Optional[Dict[str, Any]] = {}

class TryOnUpdate(BaseModel):
    session_data: Optional[Dict[str, Any]] = None
    fit_analysis: Optional[Dict[str, Any]] = None
    duration_seconds: Optional[int] = None

class TryOnResponse(BaseModel):
    id: str
    user_id: str
    store_id: str
    product_id: str
    avatar_id: Optional[str] = None
    session_data: Optional[Dict[str, Any]] = {}
    fit_analysis: Optional[Dict[str, Any]] = {}
    duration_seconds: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class FitAnalysisRequest(BaseModel):
    user_measurements: Dict[str, float]
    product_size_chart: Dict[str, Dict[str, float]]
    user_body_type: Optional[str] = "hourglass"

class FitAnalysisResponse(BaseModel):
    recommended_size: str
    confidence: float
    fit_score: float
    measurement_differences: Dict[str, float]
    size_chart_comparison: Dict[str, Dict[str, float]]
    fit_heatmap: Optional[Dict[str, str]] = None
    body_type: str
    style_compatibility: float

# Try-on session endpoints
@router.post("/", response_model=TryOnResponse, status_code=status.HTTP_201_CREATED)
async def create_tryon_session_endpoint(tryon: TryOnCreate, 
                                       current_user: User = Depends(get_current_active_user),
                                       db: Session = Depends(get_db_session)):
    """Create a new try-on session"""
    try:
        # Verify store exists
        db_store = get_store(db, tryon.store_id)
        if not db_store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        # Verify product exists
        db_product = get_product(db, tryon.product_id)
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Verify avatar exists if provided
        if tryon.avatar_id:
            db_avatar = get_user_avatar(db, tryon.avatar_id)
            if not db_avatar:
                raise HTTPException(status_code=404, detail="Avatar not found")
        
        # Create try-on session
        session_data = {
            "id": str(uuid.uuid4()),
            "user_id": current_user.id,
            "store_id": tryon.store_id,
            "product_id": tryon.product_id,
            "avatar_id": tryon.avatar_id,
            "session_data": tryon.session_data or {},
            "created_at": datetime.utcnow()
        }
        
        db_session = create_tryon_session(db, session_data)
        return db_session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating try-on session: {str(e)}")

@router.get("/", response_model=List[TryOnResponse])
async def list_tryon_sessions(skip: int = 0, limit: int = 50,
                             current_user: User = Depends(get_current_active_user),
                             db: Session = Depends(get_db_session)):
    """List try-on sessions for current user"""
    try:
        sessions = db.query(DBTryOnSession).filter(
            DBTryOnSession.user_id == current_user.id
        ).offset(skip).limit(limit).all()
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing try-on sessions: {str(e)}")

@router.get("/{session_id}", response_model=TryOnResponse)
async def get_tryon_session_endpoint(session_id: str, 
                                    current_user: User = Depends(get_current_active_user),
                                    db: Session = Depends(get_db_session)):
    """Get try-on session by ID"""
    try:
        db_session = get_tryon_session(db, session_id)
        if not db_session:
            raise HTTPException(status_code=404, detail="Try-on session not found")
        
        # Users can only access their own sessions
        if db_session.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this session")
        
        return db_session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving try-on session: {str(e)}")

@router.put("/{session_id}", response_model=TryOnResponse)
async def update_tryon_session_endpoint(session_id: str, tryon: TryOnUpdate,
                                       current_user: User = Depends(get_current_active_user),
                                       db: Session = Depends(get_db_session)):
    """Update try-on session by ID"""
    try:
        # Verify session exists
        db_session = get_tryon_session(db, session_id)
        if not db_session:
            raise HTTPException(status_code=404, detail="Try-on session not found")
        
        # Users can only update their own sessions
        if db_session.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this session")
        
        update_data = tryon.dict(exclude_unset=True)
        if update_data:
            updated_session = update_tryon_session(db, session_id, update_data)
            if not updated_session:
                raise HTTPException(status_code=404, detail="Try-on session not found")
            return updated_session
        return db_session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating try-on session: {str(e)}")

@router.delete("/{session_id}", response_model=dict)
async def delete_tryon_session_endpoint(session_id: str,
                                       current_user: User = Depends(get_current_active_user),
                                       db: Session = Depends(get_db_session)):
    """Delete try-on session by ID"""
    try:
        # Verify session exists
        db_session = get_tryon_session(db, session_id)
        if not db_session:
            raise HTTPException(status_code=404, detail="Try-on session not found")
        
        # Users can only delete their own sessions
        if db_session.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this session")
        
        success = delete_tryon_session(db, session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Try-on session not found")
        return {"message": "Try-on session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting try-on session: {str(e)}")

@router.post("/analyze-fit/", response_model=FitAnalysisResponse)
async def analyze_product_fit(fit_request: FitAnalysisRequest,
                             current_user: User = Depends(get_current_active_user)):
    """Analyze how well a product fits a user based on measurements"""
    try:
        # In a real implementation, this would use AI models to analyze fit
        # For now, we'll provide a simulated analysis
        
        user_measurements = fit_request.user_measurements
        product_size_chart = fit_request.product_size_chart
        user_body_type = fit_request.user_body_type or "hourglass"
        
        # Find the best matching size
        best_size = None
        best_score = 0
        measurement_differences = {}
        size_chart_comparison = {}
        
        for size, measurements in product_size_chart.items():
            # Calculate measurement differences
            size_diffs = {}
            size_comparison = {}
            
            for measurement, user_val in user_measurements.items():
                if measurement in measurements:
                    product_val = measurements[measurement]
                    diff = abs(user_val - product_val)
                    size_diffs[measurement] = diff
                    size_comparison[measurement] = {
                        "user": user_val,
                        "product": product_val,
                        "difference": diff
                    }
            
            # Calculate fit score based on measurement differences
            total_diff = sum(size_diffs.values())
            avg_diff = total_diff / len(size_diffs) if size_diffs else 0
            fit_score = 1.0 / (1.0 + avg_diff) if avg_diff > 0 else 1.0
            
            # Update best size if this is better
            if fit_score > best_score:
                best_score = fit_score
                best_size = size
                measurement_differences = size_diffs
                size_chart_comparison = {size: size_comparison}
        
        # Calculate confidence based on fit score
        confidence = min(1.0, best_score * 1.2)  # Boost confidence slightly
        
        # Calculate style compatibility (mock implementation)
        style_compatibility = 0.85  # Placeholder
        
        # Create fit analysis response
        from backend.ai_models_real import fit_prediction_model
        heatmap = fit_prediction_model._calculate_fit_heatmap(user_measurements, product_size_chart.get(best_size, {}))

        fit_analysis = FitAnalysisResponse(
            recommended_size=best_size or "M",
            confidence=round(confidence, 2),
            fit_score=round(best_score, 2),
            measurement_differences=measurement_differences,
            size_chart_comparison=size_chart_comparison,
            fit_heatmap=heatmap,
            body_type=user_body_type,
            style_compatibility=round(style_compatibility, 2)
        )
        
        return fit_analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing product fit: {str(e)}")

@router.post("/{session_id}/start/", response_model=TryOnResponse)
async def start_tryon_session(session_id: str,
                             current_user: User = Depends(get_current_active_user),
                             db: Session = Depends(get_db_session)):
    """Start a try-on session"""
    try:
        # Verify session exists
        db_session = get_tryon_session(db, session_id)
        if not db_session:
            raise HTTPException(status_code=404, detail="Try-on session not found")
        
        # Users can only start their own sessions
        if db_session.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to start this session")
        
        # Update session to indicate it's started
        update_data = {
            "session_data": {
                **(db_session.session_data or {}),
                "started_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
        }
        
        updated_session = update_tryon_session(db, session_id, update_data)
        return updated_session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting try-on session: {str(e)}")

@router.post("/{session_id}/end/", response_model=TryOnResponse)
async def end_tryon_session(session_id: str,
                           current_user: User = Depends(get_current_active_user),
                           db: Session = Depends(get_db_session)):
    """End a try-on session"""
    try:
        # Verify session exists
        db_session = get_tryon_session(db, session_id)
        if not db_session:
            raise HTTPException(status_code=404, detail="Try-on session not found")
        
        # Users can only end their own sessions
        if db_session.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to end this session")
        
        # Calculate session duration if not already set
        session_data = db_session.session_data or {}
        started_at_str = session_data.get("started_at")
        
        duration_seconds = None
        if started_at_str:
            try:
                started_at = datetime.fromisoformat(started_at_str)
                duration_seconds = int((datetime.utcnow() - started_at).total_seconds())
            except Exception:
                pass  # Invalid date format, leave duration as None
        
        # Update session to indicate it's ended
        update_data = {
            "session_data": {
                **session_data,
                "ended_at": datetime.utcnow().isoformat(),
                "status": "completed"
            }
        }
        
        if duration_seconds:
            update_data["duration_seconds"] = duration_seconds
        
        updated_session = update_tryon_session(db, session_id, update_data)
        return updated_session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ending try-on session: {str(e)}")

@router.get("/{session_id}/duration/")
async def get_session_duration(session_id: str,
                              current_user: User = Depends(get_current_active_user),
                              db: Session = Depends(get_db_session)):
    """Get current duration of an active try-on session"""
    try:
        # Verify session exists
        db_session = get_tryon_session(db, session_id)
        if not db_session:
            raise HTTPException(status_code=404, detail="Try-on session not found")
        
        # Users can only access their own sessions
        if db_session.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this session")
        
        # Get session duration
        session_data = db_session.session_data or {}
        started_at_str = session_data.get("started_at")
        
        if not started_at_str:
            return {"duration_seconds": 0, "status": "not_started"}
        
        try:
            started_at = datetime.fromisoformat(started_at_str)
            duration_seconds = int((datetime.utcnow() - started_at).total_seconds())
            return {"duration_seconds": duration_seconds, "status": session_data.get("status", "unknown")}
        except Exception:
            return {"duration_seconds": 0, "status": "invalid_timestamp"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting session duration: {str(e)}")