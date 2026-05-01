# api/avatars.py
# Avatar management API endpoints for Aetherstore Engine

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import os
from sqlalchemy.orm import Session
from models import UserAvatar as DBUserAvatar, User
from crud import get_user_avatar, create_user_avatar, update_user_avatar, delete_user_avatar
from crud import get_user
from auth import get_current_active_user
from database import get_db_session

router = APIRouter()

# Pydantic models for request/response
class AvatarCreate(BaseModel):
    scan_data_url: Optional[str] = None
    measurements: Optional[Dict[str, Any]] = {}
    body_type: Optional[str] = None
    avatar_3d_url: Optional[str] = None

class AvatarUpdate(BaseModel):
    scan_data_url: Optional[str] = None
    measurements: Optional[Dict[str, Any]] = None
    body_type: Optional[str] = None
    avatar_3d_url: Optional[str] = None

class AvatarResponse(BaseModel):
    id: str
    user_id: str
    scan_data_url: Optional[str] = None
    measurements: Optional[Dict[str, Any]] = {}
    body_type: Optional[str] = None
    avatar_3d_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)