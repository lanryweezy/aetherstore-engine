# payment_service_brand.py
# Payment service for brand stores (uses brand's own payment keys)

import stripe
import requests
from typing import Dict, Any, Optional
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class BrandPaymentService:
    """Payment service that uses brand-specific payment gateway credentials"""
    
    def __init__(self, provider: str, public_key: str, secret_key: str, webhook_secret: Optional[str] = None):
        """
        Initialize payment service with brand's credentials
        
        Args:
            provider: "stripe" or "paystack"
            public_key: Brand's public key
            secret_key: Brand's secret key
            webhook_secret: Webhook secret for verification
        """
        self.provider = provider.lower()
        self.public_key = public_key
        self.secret_key = secret_key
        self.webhook_secret = webhook_secret
        
        if self.provider == "stripe":
            stripe.api_key = secret_key
            self.paystack_base_url = None
        elif self.provider == "paystack":
            self.paystack_base_url = "https://api.paystack.co"
        else:
            raise ValueError(f"Unsupported payment provider: {provider}")
    
    async def create_payment_intent(
        self,
        amount: float,
        currency: str = "usd",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a payment intent using brand's Stripe account"""
        if self.provider != "stripe":
            raise HTTPException(
                status_code=400,
                detail="This method is only for Stripe"
            )
        
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),
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
                "status": intent.status,
                "public_key": self.public_key
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Stripe payment error: {str(e)}"
            )
    
    async def initialize_payment(
        self,
        email: str,
        amount: float,
        currency: str = "NGN",
        reference: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Initialize a Paystack payment using brand's account"""
        if self.provider != "paystack":
            raise HTTPException(
                status_code=400,
                detail="This method is only for Paystack"
            )
        
        try:
            url = f"{self.paystack_base_url}/transaction/initialize"
            headers = {
                "Authorization": f"Bearer {self.secret_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "email": email,
                "amount": int(amount * 100),
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
                    "currency": currency,
                    "public_key": self.public_key
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
    
    async def verify_payment(self, payment_id: str) -> Dict[str, Any]:
        """Verify a payment"""
        if self.provider == "stripe":
            try:
                intent = stripe.PaymentIntent.retrieve(payment_id)
                return {
                    "success": intent.status == "succeeded",
                    "payment_id": intent.id,
                    "amount": intent.amount / 100,
                    "currency": intent.currency,
                    "status": intent.status
                }
            except stripe.error.StripeError as e:
                logger.error(f"Stripe error: {str(e)}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Stripe payment error: {str(e)}"
                )
        
        elif self.provider == "paystack":
            try:
                url = f"{self.paystack_base_url}/transaction/verify/{payment_id}"
                headers = {
                    "Authorization": f"Bearer {self.secret_key}",
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
                        "status": data["data"]["status"]
                    }
                else:
                    return {
                        "success": False,
                        "reference": payment_id,
                        "status": data["data"].get("status", "failed")
                    }
            except requests.exceptions.RequestException as e:
                logger.error(f"Paystack API error: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error verifying Paystack payment: {str(e)}"
                )
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported provider: {self.provider}"
            )

def get_brand_payment_service(brand_settings: Dict[str, Any], provider: str = "stripe") -> Optional[BrandPaymentService]:
    """
    Get payment service for a brand
    
    Args:
        brand_settings: Brand's settings dict containing payment_gateways
        provider: "stripe" or "paystack"
    
    Returns:
        BrandPaymentService instance or None if not configured
    """
    payment_gateways = brand_settings.get("payment_gateways", {})
    gateway_config = payment_gateways.get(provider.lower())
    
    if not gateway_config or not gateway_config.get("is_active"):
        return None
    
    return BrandPaymentService(
        provider=provider,
        public_key=gateway_config.get("public_key"),
        secret_key=gateway_config.get("secret_key"),
        webhook_secret=gateway_config.get("webhook_secret")
    )

