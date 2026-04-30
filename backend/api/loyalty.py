# api/loyalty.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import UserLoyalty, LoyaltyTransaction
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

router = APIRouter()

class LoyaltyResponse(BaseModel):
    user_id: str
    points_balance: int
    tier: str
    total_earned: int
    last_activity: datetime

    model_config = ConfigDict(from_attributes=True)

class TransactionResponse(BaseModel):
    id: str
    amount: int
    reason: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

@router.get("/{user_id}", response_model=LoyaltyResponse)
async def get_user_loyalty(user_id: str, db: Session = Depends(get_db)):
    loyalty = db.query(UserLoyalty).filter(UserLoyalty.user_id == user_id).first()
    if not loyalty:
        # Initialize loyalty for user if not exists
        loyalty = UserLoyalty(user_id=user_id)
        db.add(loyalty)
        db.commit()
        db.refresh(loyalty)
    return loyalty

@router.get("/{user_id}/transactions", response_model=List[TransactionResponse])
async def get_loyalty_transactions(user_id: str, db: Session = Depends(get_db)):
    return db.query(LoyaltyTransaction).filter(LoyaltyTransaction.user_id == user_id).order_by(LoyaltyTransaction.timestamp.desc()).all()

@router.post("/{user_id}/earn")
async def earn_points(user_id: str, amount: int, reason: str, db: Session = Depends(get_db)):
    loyalty = db.query(UserLoyalty).filter(UserLoyalty.user_id == user_id).first()
    if not loyalty:
        loyalty = UserLoyalty(user_id=user_id)
        db.add(loyalty)

    loyalty.points_balance += amount
    loyalty.total_earned += amount
    loyalty.last_activity = datetime.now()

    # Update tier
    if loyalty.total_earned > 5000:
        loyalty.tier = "platinum"
    elif loyalty.total_earned > 2000:
        loyalty.tier = "gold"
    elif loyalty.total_earned > 500:
        loyalty.tier = "silver"

    transaction = LoyaltyTransaction(user_id=user_id, amount=amount, reason=reason)
    db.add(transaction)
    db.commit()

    return {"success": True, "new_balance": loyalty.points_balance, "tier": loyalty.tier}
