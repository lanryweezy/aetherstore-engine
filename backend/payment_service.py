# payment_service.py
# Payment processing service for Stripe and Paystack integration

import stripe
import requests
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
import logging
from config import settings

logger = logging.getLogger(__name__)

class PaymentService:
    """Unified payment service for Stripe and Paystack"""
    
    def __init__(self):
        # Initialize Stripe
        self.stripe_secret_key = settings.STRIPE_SECRET_KEY
        if self.stripe_secret_key:
            stripe.api_key = self.stripe_secret_key
        
        # Initialize Paystack
        self.paystack_secret_key = settings.PAYSTACK_SECRET_KEY
        self.paystack_public_key = settings.PAYSTACK_PUBLIC_KEY
        self.paystack_base_url = "https://api.paystack.co"
    
    async def create_payment_intent_stripe(
        self, 
        amount: float, 
        currency: str = "usd",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a Stripe payment intent"""
        try:
            if not self.stripe_secret_key:
                raise HTTPException(
                    status_code=500,
                    detail="Stripe is not configured. Please set STRIPE_SECRET_KEY."
                )
            
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency.lower(),
                metadata=metadata or {},
                automatic_payment_methods={
                    'enabled': True,
                },
            )
            
            return {
                "payment_intent_id": intent.id,
                "client_secret": intent.client_secret,
                "amount": amount,
                "currency": currency,
                "status": intent.status
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Stripe payment error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error creating Stripe payment intent: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error creating payment intent: {str(e)}"
            )
    
    async def confirm_payment_stripe(self, payment_intent_id: str) -> Dict[str, Any]:
        """Confirm a Stripe payment"""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if intent.status == 'succeeded':
                return {
                    "success": True,
                    "payment_intent_id": intent.id,
                    "amount": intent.amount / 100,
                    "currency": intent.currency,
                    "status": intent.status
                }
            else:
                return {
                    "success": False,
                    "payment_intent_id": intent.id,
                    "status": intent.status,
                    "message": f"Payment status: {intent.status}"
                }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Stripe payment error: {str(e)}"
            )
    
    async def create_payment_paystack(
        self,
        email: str,
        amount: float,
        currency: str = "NGN",
        reference: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a Paystack payment"""
        try:
            if not self.paystack_secret_key:
                raise HTTPException(
                    status_code=500,
                    detail="Paystack is not configured. Please set PAYSTACK_SECRET_KEY."
                )
            
            url = f"{self.paystack_base_url}/transaction/initialize"
            headers = {
                "Authorization": f"Bearer {self.paystack_secret_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "email": email,
                "amount": int(amount * 100),  # Convert to kobo/cents
                "currency": currency.upper(),
                "reference": reference,
                "metadata": metadata or {}
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status"):
                return {
                    "success": True,
                    "authorization_url": data["data"]["authorization_url"],
                    "access_code": data["data"]["access_code"],
                    "reference": data["data"]["reference"],
                    "amount": amount,
                    "currency": currency
                }
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Paystack error: {data.get('message', 'Unknown error')}"
                )
        except requests.exceptions.RequestException as e:
            logger.error(f"Paystack API error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error connecting to Paystack: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error creating Paystack payment: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error creating payment: {str(e)}"
            )
    
    async def verify_payment_paystack(self, reference: str) -> Dict[str, Any]:
        """Verify a Paystack payment"""
        try:
            if not self.paystack_secret_key:
                raise HTTPException(
                    status_code=500,
                    detail="Paystack is not configured."
                )
            
            url = f"{self.paystack_base_url}/transaction/verify/{reference}"
            headers = {
                "Authorization": f"Bearer {self.paystack_secret_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") and data["data"]["status"] == "success":
                return {
                    "success": True,
                    "reference": data["data"]["reference"],
                    "amount": data["data"]["amount"] / 100,
                    "currency": data["data"]["currency"],
                    "status": data["data"]["status"],
                    "paid_at": data["data"]["paid_at"]
                }
            else:
                return {
                    "success": False,
                    "reference": reference,
                    "status": data["data"].get("status", "failed"),
                    "message": data.get("message", "Payment verification failed")
                }
        except requests.exceptions.RequestException as e:
            logger.error(f"Paystack API error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error verifying Paystack payment: {str(e)}"
            )
    
    async def refund_payment_stripe(self, payment_intent_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """Refund a Stripe payment"""
        try:
            if not self.stripe_secret_key:
                raise HTTPException(
                    status_code=500,
                    detail="Stripe is not configured."
                )
            
            refund_params = {"payment_intent": payment_intent_id}
            if amount:
                refund_params["amount"] = int(amount * 100)
            
            refund = stripe.Refund.create(**refund_params)
            
            return {
                "success": True,
                "refund_id": refund.id,
                "amount": refund.amount / 100,
                "status": refund.status
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe refund error: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Stripe refund error: {str(e)}"
            )
    
    async def refund_payment_paystack(self, transaction_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """Refund a Paystack payment"""
        try:
            if not self.paystack_secret_key:
                raise HTTPException(
                    status_code=500,
                    detail="Paystack is not configured."
                )
            
            url = f"{self.paystack_base_url}/refund"
            headers = {
                "Authorization": f"Bearer {self.paystack_secret_key}",
                "Content-Type": "application/json"
            }
            
            payload = {"transaction": transaction_id}
            if amount:
                payload["amount"] = int(amount * 100)
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status"):
                return {
                    "success": True,
                    "refund_id": data["data"]["id"],
                    "amount": data["data"]["amount"] / 100,
                    "status": data["data"]["status"]
                }
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Paystack refund error: {data.get('message', 'Unknown error')}"
                )
        except requests.exceptions.RequestException as e:
            logger.error(f"Paystack API error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error processing Paystack refund: {str(e)}"
            )

# Global payment service instance
payment_service = PaymentService()

