# api/users.py
# User management API endpoints for Aetherstore Engine

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
import uuid

from security_middleware import limiter
from auth import authenticate_user, create_access_token, get_password_hash
from sqlalchemy.orm import Session
from database import get_db
from crud import get_user_by_email, create_user
from email_service import email_service

router = APIRouter()

# Pydantic models for request/response
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

@router.post("/register", response_model=UserResponse)
@limiter.limit("5/minute")
async def register_user(request: Request, user_in: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    user_data = user_in.dict()
    user_data["password_hash"] = get_password_hash(user_data.pop("password"))
    new_user = create_user(db, user_data=user_data)

    # Background: Send welcome email
    try:
        await email_service.send_welcome_email(new_user.email, new_user.name)
    except Exception as e:
        print(f"Non-blocking email error: {e}")

    return new_user

@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(request: Request, user_in: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_in.email, user_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

from models import UserActivity
class ActivityCreate(BaseModel):
    activity_type: str
    product_id: Optional[str] = None
    store_id: Optional[str] = None
    metadata_json: Optional[dict] = {}

@router.post("/{user_id}/activity")
async def track_user_activity(user_id: str, activity_in: ActivityCreate, db: Session = Depends(get_db)):
    new_activity = UserActivity(
        user_id=user_id,
        activity_type=activity_in.activity_type,
        product_id=activity_in.product_id,
        store_id=activity_in.store_id,
        metadata_json=activity_in.metadata_json
    )
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    return {"success": True, "activity_id": str(new_activity.id)}

@router.get("/{user_id}/recent-activity")
async def get_recent_activity(user_id: str, limit: int = 10, db: Session = Depends(get_db)):
    activities = db.query(UserActivity).filter(UserActivity.user_id == user_id).order_by(UserActivity.timestamp.desc()).limit(limit).all()
    return [{"id": str(a.id), "type": a.activity_type, "product_id": a.product_id, "store_id": a.store_id, "timestamp": a.timestamp} for a in activities]
