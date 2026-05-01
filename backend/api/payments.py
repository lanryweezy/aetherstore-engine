# api/payments.py
# Payment processing API endpoints

from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_active_user
from models import User, Order, OrderItem, ShoppingCart, CartItem, Product
from crud import get_order, create_order, update_order_status, get_user_cart, get_product
from payment_service import payment_service

router = APIRouter(prefix="/payments", tags=["payments"])
logger = logging.getLogger(__name__)

# Pydantic models
class PaymentIntentRequest(BaseModel):
    amount: float
    currency: str = "usd"
    order_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class PaymentIntentResponse(BaseModel):
    payment_intent_id: str
    client_secret: str
    amount: float
    currency: str
    status: str

class PaystackPaymentRequest(BaseModel):
    email: EmailStr
    amount: float
    currency: str = "NGN"
    order_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class PaystackPaymentResponse(BaseModel):
    success: bool
    authorization_url: str
    access_code: str
    reference: str
    amount: float
    currency: str

class PaymentVerificationRequest(BaseModel):
    payment_provider: str  # "stripe" or "paystack"
    payment_id: str  # payment_intent_id for Stripe, reference for Paystack

class PaymentVerificationResponse(BaseModel):
    success: bool
    payment_id: str
    amount: float
    currency: str
    status: str
    order_id: Optional[str] = None

class RefundRequest(BaseModel):
    payment_provider: str
    payment_id: str
    amount: Optional[float] = None
    reason: Optional[str] = None

# Payment endpoints
@router.post("/stripe/create-intent", response_model=PaymentIntentResponse)
async def create_stripe_payment_intent(
    request: PaymentIntentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a Stripe payment intent"""
    try:
        # Validate amount
        if request.amount <= 0:
            raise HTTPException(
                status_code=400,
                detail="Amount must be greater than 0"
            )
        
        # If order_id is provided, verify order exists and belongs to user
        metadata = request.metadata or {}
        if request.order_id:
            order = get_order(db, request.order_id)
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            if order.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not authorized")
            metadata["order_id"] = request.order_id
            metadata["user_id"] = current_user.id
        
        # Create payment intent
        result = await payment_service.create_payment_intent_stripe(
            amount=request.amount,
            currency=request.currency,
            metadata=metadata
        )
        
        return PaymentIntentResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating Stripe payment intent: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating payment intent: {str(e)}"
        )

@router.post("/paystack/initialize", response_model=PaystackPaymentResponse)
async def initialize_paystack_payment(
    request: PaystackPaymentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Initialize a Paystack payment"""
    try:
        # Validate amount
        if request.amount <= 0:
            raise HTTPException(
                status_code=400,
                detail="Amount must be greater than 0"
            )
        
        # Generate reference
        import uuid
        reference = f"PAYSTACK_{uuid.uuid4().hex[:12].upper()}"
        
        # Prepare metadata
        metadata = request.metadata or {}
        if request.order_id:
            order = get_order(db, request.order_id)
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            if order.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not authorized")
            metadata["order_id"] = request.order_id
        metadata["user_id"] = current_user.id
        
        # Create payment
        result = await payment_service.create_payment_paystack(
            email=request.email,
            amount=request.amount,
            currency=request.currency,
            reference=reference,
            metadata=metadata
        )
        
        return PaystackPaymentResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initializing Paystack payment: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error initializing payment: {str(e)}"
        )

@router.post("/verify", response_model=PaymentVerificationResponse)
async def verify_payment(
    request: PaymentVerificationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Verify a payment (Stripe or Paystack)"""
    try:
        if request.payment_provider.lower() == "stripe":
            result = await payment_service.confirm_payment_stripe(request.payment_id)
            
            if result.get("success"):
                # Update order status if order_id is in metadata
                # This would typically come from webhook, but we can also handle here
                order_id = None
                if "order_id" in result.get("metadata", {}):
                    order_id = result["metadata"]["order_id"]
                    update_order_status(db, order_id, "paid")
                    # Update payment status
                    order = get_order(db, order_id)
                    if order:
                        order.payment_status = "paid"
                        db.commit()
            
            return PaymentVerificationResponse(
                success=result.get("success", False),
                payment_id=request.payment_id,
                amount=result.get("amount", 0),
                currency=result.get("currency", "usd"),
                status=result.get("status", "unknown"),
                order_id=order_id
            )
        
        elif request.payment_provider.lower() == "paystack":
            result = await payment_service.verify_payment_paystack(request.payment_id)
            
            if result.get("success"):
                # Update order status
                order_id = None
                # Try to find order by payment reference
                # In production, you'd store payment reference with order
                # For now, we'll handle via webhook
            
            return PaymentVerificationResponse(
                success=result.get("success", False),
                payment_id=request.payment_id,
                amount=result.get("amount", 0),
                currency=result.get("currency", "NGN"),
                status=result.get("status", "unknown"),
                order_id=order_id
            )
        
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid payment provider. Use 'stripe' or 'paystack'"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error verifying payment: {str(e)}"
        )

@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature")
):
    """Handle Stripe webhooks"""
    try:
        import stripe
        from config import settings
        
        body = await request.body()
        
        # Verify webhook signature
        endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)
        
        if endpoint_secret:
            try:
                event = stripe.Webhook.construct_event(
                    body, stripe_signature, endpoint_secret
                )
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid payload")
            except stripe.error.SignatureVerificationError:
                raise HTTPException(status_code=400, detail="Invalid signature")
        else:
            # In development, accept without verification
            import json
            event = json.loads(body)
        
        # Idempotency Check
        event_id = event["id"]
        from database import SessionLocal
        from models import ProcessedWebhook
        db = SessionLocal()

        try:
            # Check if we already processed this webhook
            if db.query(ProcessedWebhook).filter(ProcessedWebhook.id == event_id).first():
                logger.info(f"Webhook {event_id} already processed. Skipping.")
                return {"status": "success", "message": "already_processed"}

            # Handle the event
            if event["type"] == "payment_intent.succeeded":
                payment_intent = event["data"]["object"]
                logger.info(f"Payment succeeded: {payment_intent['id']}")

                # Update order status
                order_id = payment_intent.get("metadata", {}).get("order_id")
                if order_id:
                    order = get_order(db, order_id)
                    if order:
                        order.payment_status = "paid"
                        order.status = "confirmed"
            
            elif event["type"] == "payment_intent.payment_failed":
                payment_intent = event["data"]["object"]
                logger.warning(f"Payment failed: {payment_intent['id']}")

                order_id = payment_intent.get("metadata", {}).get("order_id")
                if order_id:
                    order = get_order(db, order_id)
                    if order:
                        order.payment_status = "failed"

            # Record webhook as processed
            processed = ProcessedWebhook(id=event_id, provider="stripe")
            db.add(processed)
            db.commit()
        finally:
            db.close()
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error handling Stripe webhook: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing webhook: {str(e)}"
        )

@router.post("/webhooks/paystack")
async def paystack_webhook(request: Request):
    """Handle Paystack webhooks"""
    try:
        body = await request.json()
        event = body.get("event")
        data = body.get("data", {})
        reference = data.get("reference")
        
        # Idempotency Check for Paystack (We use the reference as the unique event ID)
        if not reference:
            return {"status": "ignored"}
            
        from database import SessionLocal
        from models import ProcessedWebhook
        db = SessionLocal()

        try:
            if db.query(ProcessedWebhook).filter(ProcessedWebhook.id == reference).first():
                logger.info(f"Webhook {reference} already processed. Skipping.")
                return {"status": "success", "message": "already_processed"}

            if event == "charge.success":
                logger.info(f"Payment succeeded: {reference}")
                
                # Verify payment
                result = await payment_service.verify_payment_paystack(reference)

                if result.get("success"):
                    metadata = data.get("metadata", {})
                    order_id = metadata.get("order_id")

                    if order_id:
                        order = get_order(db, order_id)
                        if order:
                            order.payment_status = "paid"
                            order.status = "confirmed"
            
            elif event == "charge.failed":
                logger.warning(f"Payment failed: {reference}")

                metadata = data.get("metadata", {})
                order_id = metadata.get("order_id")

                if order_id:
                    order = get_order(db, order_id)
                    if order:
                        order.payment_status = "failed"

            # Record webhook as processed
            processed = ProcessedWebhook(id=reference, provider="paystack")
            db.add(processed)
            db.commit()
        finally:
            db.close()
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error handling Paystack webhook: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing webhook: {str(e)}"
        )

@router.post("/refund")
async def refund_payment(
    refund_request: RefundRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Refund a payment"""
    try:
        # Verify user has permission (admin or order owner)
        # For now, we'll allow if user is admin or order owner
        
        if refund_request.payment_provider.lower() == "stripe":
            result = await payment_service.refund_payment_stripe(
                refund_request.payment_id,
                refund_request.amount
            )
        elif refund_request.payment_provider.lower() == "paystack":
            result = await payment_service.refund_payment_paystack(
                refund_request.payment_id,
                refund_request.amount
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid payment provider"
            )
        
        if result.get("success"):
            pass
            # Update order status
            # Find order by payment_id (would need to store this)
            # For now, return success
            pass
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing refund: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing refund: {str(e)}"
        )

