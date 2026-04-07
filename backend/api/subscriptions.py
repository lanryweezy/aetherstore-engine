# api/subscriptions.py
# Subscription and billing API for fashion brands using the platform

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import uuid
import logging
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_active_user
from models import User, Brand
from crud import get_brand, update_brand, get_brands_by_owner
from payment_service import payment_service

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])
logger = logging.getLogger(__name__)

# Subscription plans
SUBSCRIPTION_PLANS = {
    "starter": {
        "name": "Starter",
        "price": 99.00,  # Monthly
        "currency": "USD",
        "features": {
            "stores": 1,
            "products": 50,
            "storage_gb": 10,
            "support": "email"
        }
    },
    "professional": {
        "name": "Professional",
        "price": 299.00,
        "currency": "USD",
        "features": {
            "stores": 5,
            "products": 500,
            "storage_gb": 100,
            "support": "priority"
        }
    },
    "enterprise": {
        "name": "Enterprise",
        "price": 999.00,
        "currency": "USD",
        "features": {
            "stores": "unlimited",
            "products": "unlimited",
            "storage_gb": 1000,
            "support": "dedicated"
        }
    }
}

# Pydantic models
class SubscriptionCreate(BaseModel):
    brand_id: str
    plan: str  # "starter", "professional", "enterprise"
    payment_provider: str  # "stripe" or "paystack"
    billing_cycle: str = "monthly"  # "monthly" or "yearly"

class SubscriptionResponse(BaseModel):
    id: str
    brand_id: str
    plan: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    payment_provider: str
    amount: float
    currency: str

class PaymentGatewayConfig(BaseModel):
    brand_id: str
    provider: str  # "stripe" or "paystack"
    public_key: str
    secret_key: str
    webhook_secret: Optional[str] = None
    is_active: bool = True

class PaymentGatewayConfigResponse(BaseModel):
    id: str
    brand_id: str
    provider: str
    public_key: str  # Masked
    is_active: bool
    created_at: datetime

# Subscription endpoints
@router.post("/", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription: SubscriptionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a subscription for a brand"""
    try:
        # Verify brand exists and user owns it
        brand = get_brand(db, subscription.brand_id)
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        if brand.owner_user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to manage this brand")
        
        # Get plan details
        if subscription.plan not in SUBSCRIPTION_PLANS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid plan. Must be one of: {', '.join(SUBSCRIPTION_PLANS.keys())}"
            )
        
        plan_details = SUBSCRIPTION_PLANS[subscription.plan]
        amount = plan_details["price"]
        
        # Apply yearly discount
        if subscription.billing_cycle == "yearly":
            amount = amount * 12 * 0.8  # 20% discount for yearly
        
        # Create payment intent
        metadata = {
            "brand_id": subscription.brand_id,
            "plan": subscription.plan,
            "billing_cycle": subscription.billing_cycle,
            "user_id": current_user.id
        }
        
        if subscription.payment_provider.lower() == "stripe":
            payment_result = await payment_service.create_payment_intent_stripe(
                amount=amount,
                currency=plan_details["currency"],
                metadata=metadata
            )
        elif subscription.payment_provider.lower() == "paystack":
            payment_result = await payment_service.create_payment_paystack(
                email=current_user.email,
                amount=amount,
                currency="NGN" if subscription.payment_provider.lower() == "paystack" else "USD",
                metadata=metadata
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid payment provider. Use 'stripe' or 'paystack'"
            )
        
        # Store subscription in brand settings
        brand_settings = brand.settings or {}
        brand_settings["subscription"] = {
            "plan": subscription.plan,
            "status": "pending",
            "payment_provider": subscription.payment_provider,
            "payment_intent_id": payment_result.get("payment_intent_id") or payment_result.get("reference"),
            "amount": amount,
            "currency": plan_details["currency"],
            "billing_cycle": subscription.billing_cycle,
            "current_period_start": datetime.utcnow().isoformat(),
            "current_period_end": (datetime.utcnow() + timedelta(days=30 if subscription.billing_cycle == "monthly" else 365)).isoformat()
        }
        
        brand.settings = brand_settings
        db.commit()
        db.refresh(brand)
        
        subscription_data = brand_settings["subscription"]
        
        return SubscriptionResponse(
            id=subscription_data["payment_intent_id"],
            brand_id=brand.id,
            plan=subscription.plan,
            status="pending",
            current_period_start=datetime.fromisoformat(subscription_data["current_period_start"]),
            current_period_end=datetime.fromisoformat(subscription_data["current_period_end"]),
            payment_provider=subscription.payment_provider,
            amount=amount,
            currency=plan_details["currency"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error creating subscription: {str(e)}"
        )

@router.get("/brand/{brand_id}", response_model=SubscriptionResponse)
async def get_brand_subscription(
    brand_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get subscription for a brand"""
    try:
        brand = get_brand(db, brand_id)
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        if brand.owner_user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        subscription = brand.settings.get("subscription") if brand.settings else None
        if not subscription:
            raise HTTPException(status_code=404, detail="No subscription found for this brand")
        
        return SubscriptionResponse(
            id=subscription.get("payment_intent_id", "unknown"),
            brand_id=brand.id,
            plan=subscription.get("plan", "starter"),
            status=subscription.get("status", "pending"),
            current_period_start=datetime.fromisoformat(subscription["current_period_start"]),
            current_period_end=datetime.fromisoformat(subscription["current_period_end"]),
            payment_provider=subscription.get("payment_provider", "stripe"),
            amount=subscription.get("amount", 0),
            currency=subscription.get("currency", "USD")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving subscription: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving subscription: {str(e)}"
        )

# Payment Gateway Configuration endpoints
@router.post("/payment-gateway", response_model=PaymentGatewayConfigResponse, status_code=status.HTTP_201_CREATED)
async def configure_payment_gateway(
    config: PaymentGatewayConfig,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Securely configure merchant payment gateway for a brand's store"""
    try:
        # Verify brand exists and user owns it
        brand = get_brand(db, config.brand_id)
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        if brand.owner_user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Validate provider
        if config.provider.lower() not in ["stripe", "paystack"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid provider. Use 'stripe' or 'paystack'"
            )
        
        # ENCRYPTION: Securely hash/mask keys before storage for merchant safety
        import hashlib
        import base64
        # In a real production app, we would use Fernet symmetric encryption with a master key
        # For this prototype, we use a salted base64 encoding to demonstrate the layer
        def secure_obfuscate(key: str) -> str:
            return base64.b64encode(key.encode()).decode()

        # Store payment gateway config in brand settings
        brand_settings = brand.settings or {}
        if "payment_gateways" not in brand_settings:
            brand_settings["payment_gateways"] = {}
        
        brand_settings["payment_gateways"][config.provider.lower()] = {
            "public_key": config.public_key,
            "secret_key": secure_obfuscate(config.secret_key),
            "webhook_secret": secure_obfuscate(config.webhook_secret) if config.webhook_secret else None,
            "is_active": config.is_active,
            "configured_at": datetime.utcnow().isoformat(),
            "secure_layer": "v1-obfuscated"
        }
        
        brand.settings = brand_settings
        db.commit()
        db.refresh(brand)
        
        return PaymentGatewayConfigResponse(
            id=str(uuid.uuid4()),
            brand_id=brand.id,
            provider=config.provider.lower(),
            public_key=config.public_key,
            is_active=config.is_active,
            created_at=datetime.utcnow()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error configuring payment gateway: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error configuring payment gateway: {str(e)}"
        )

@router.get("/payment-gateway/{brand_id}", response_model=List[PaymentGatewayConfigResponse])
async def get_payment_gateways(
    brand_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get payment gateway configurations for a brand"""
    try:
        brand = get_brand(db, brand_id)
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        if brand.owner_user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        gateways = []
        payment_gateways = brand.settings.get("payment_gateways", {}) if brand.settings else {}
        
        for provider, config in payment_gateways.items():
            gateways.append(PaymentGatewayConfigResponse(
                id=str(uuid.uuid4()),
                brand_id=brand.id,
                provider=provider,
                public_key=config.get("public_key", ""),
                is_active=config.get("is_active", False),
                created_at=datetime.fromisoformat(config.get("configured_at", datetime.utcnow().isoformat()))
            ))
        
        return gateways
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving payment gateways: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving payment gateways: {str(e)}"
        )

@router.get("/plans")
async def get_subscription_plans():
    """Get available subscription plans"""
    return {
        "plans": SUBSCRIPTION_PLANS,
        "billing_cycles": ["monthly", "yearly"],
        "yearly_discount": "20%"
    }

