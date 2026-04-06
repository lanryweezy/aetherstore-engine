# api/orders.py
# Order management API endpoints

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import logging
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_active_user
from models import User, Order, OrderItem, ShoppingCart, CartItem, Product
from crud import (
    get_order, create_order, update_order_status, get_user_cart,
    get_product, get_or_create_user_cart, add_item_to_cart,
    remove_item_from_cart, get_brand, get_store
)
from payment_service_brand import get_brand_payment_service

router = APIRouter(prefix="/orders", tags=["orders"])
logger = logging.getLogger(__name__)

# Pydantic models
class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str
    country: str
    phone: Optional[str] = None

class OrderItemCreate(BaseModel):
    product_id: str
    quantity: int
    size: Optional[str] = None
    color: Optional[str] = None

class OrderCreate(BaseModel):
    cart_id: Optional[str] = None
    items: Optional[List[OrderItemCreate]] = None
    shipping_address: Address
    billing_address: Optional[Address] = None
    payment_method: str  # "stripe" or "paystack"

class OrderResponse(BaseModel):
    id: str
    user_id: str
    total_amount: float
    status: str
    payment_status: str
    payment_method: Optional[str] = None
    shipping_address: Dict[str, Any]
    billing_address: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[Dict[str, Any]] = []

    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: str  # pending, confirmed, paid, shipped, delivered, cancelled

# Order endpoints
@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order_endpoint(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new order from cart or items"""
    try:
        total_amount = 0.0
        order_items_data = []
        
        # Get items from cart or provided items
        if order_data.cart_id:
            # Get cart items
            cart = db.query(ShoppingCart).filter(
                ShoppingCart.id == order_data.cart_id,
                ShoppingCart.user_id == current_user.id
            ).first()
            
            if not cart:
                raise HTTPException(status_code=404, detail="Cart not found")
            
            cart_items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
            
            for cart_item in cart_items:
                product = get_product(db, cart_item.product_id)
                if not product:
                    continue
                
                if product.stock_quantity < cart_item.quantity:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Insufficient stock for product {product.name}"
                    )
                
                item_price = product.price * cart_item.quantity
                total_amount += item_price
                
                order_items_data.append({
                    "product_id": cart_item.product_id,
                    "quantity": cart_item.quantity,
                    "price_at_time": product.price,
                    "size": cart_item.selected_size,
                    "color": cart_item.selected_color
                })
        
        elif order_data.items:
            # Use provided items
            for item_data in order_data.items:
                product = get_product(db, item_data.product_id)
                if not product:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Product {item_data.product_id} not found"
                    )
                
                if product.stock_quantity < item_data.quantity:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Insufficient stock for product {product.name}"
                    )
                
                item_price = product.price * item_data.quantity
                total_amount += item_price
                
                order_items_data.append({
                    "product_id": item_data.product_id,
                    "quantity": item_data.quantity,
                    "price_at_time": product.price,
                    "size": item_data.size,
                    "color": item_data.color
                })
        else:
            raise HTTPException(
                status_code=400,
                detail="Either cart_id or items must be provided"
            )
        
        if total_amount <= 0:
            raise HTTPException(
                status_code=400,
                detail="Order total must be greater than 0"
            )
        
        # Use billing address if not provided
        billing_address = order_data.billing_address
        if not billing_address:
            billing_address = order_data.shipping_address
        
        # Create order
        order_data_dict = {
            "id": str(uuid.uuid4()),
            "user_id": current_user.id,
            "cart_id": order_data.cart_id,
            "total_amount": total_amount,
            "status": "pending",
            "payment_status": "pending",
            "payment_method": order_data.payment_method,
            "shipping_address": order_data.shipping_address.dict(),
            "billing_address": billing_address.dict(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        db_order = create_order(db, order_data_dict)
        
        # Create order items
        for item_data in order_items_data:
            order_item = OrderItem(
                id=str(uuid.uuid4()),
                order_id=db_order.id,
                product_id=item_data["product_id"],
                quantity=item_data["quantity"],
                price_at_time=item_data["price_at_time"],
                size=item_data.get("size"),
                color=item_data.get("color"),
                created_at=datetime.utcnow()
            )
            db.add(order_item)
            
            # Deduct inventory
            product = get_product(db, item_data["product_id"])
            if product:
                product.stock_quantity -= item_data["quantity"]
        
        db.commit()
        db.refresh(db_order)

        # DIGITAL WARDROBE INTEGRATION:
        # Automatically add purchased items to user's virtual wardrobe
        from ai_consultant import AIConsultantService
        consultant_service = AIConsultantService()
        for item_data in order_items_data:
            product = get_product(db, item_data["product_id"])
            if product:
                # We use a background task in a real app, but for now direct call
                await consultant_service.add_wardrobe_item(
                    user_id=current_user.id,
                    name=product.name,
                    category=product.category or "unspecified",
                    color=item_data.get("color") or "original",
                    brand=product.brand.name if product.brand else "Unknown",
                    style_tags=[product.category] if product.category else []
                )
        
        # Get order items for response
        order_items = db.query(OrderItem).filter(OrderItem.order_id == db_order.id).all()
        items_response = []
        for item in order_items:
            product = get_product(db, item.product_id)
            items_response.append({
                "id": item.id,
                "product_id": item.product_id,
                "product_name": product.name if product else "Unknown",
                "quantity": item.quantity,
                "price": item.price_at_time,
                "size": item.size,
                "color": item.color
            })
        
        return OrderResponse(
            id=db_order.id,
            user_id=db_order.user_id,
            total_amount=db_order.total_amount,
            status=db_order.status,
            payment_status=db_order.payment_status,
            payment_method=db_order.payment_method,
            shipping_address=db_order.shipping_address,
            billing_address=db_order.billing_address,
            created_at=db_order.created_at,
            updated_at=db_order.updated_at,
            items=items_response
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error creating order: {str(e)}"
        )

@router.get("/", response_model=List[OrderResponse])
async def list_orders(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List orders for current user"""
    try:
        orders = db.query(Order).filter(
            Order.user_id == current_user.id
        ).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
        
        orders_response = []
        for order in orders:
            order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
            items_response = []
            for item in order_items:
                product = get_product(db, item.product_id)
                items_response.append({
                    "id": item.id,
                    "product_id": item.product_id,
                    "product_name": product.name if product else "Unknown",
                    "quantity": item.quantity,
                    "price": item.price_at_time,
                    "size": item.size,
                    "color": item.color
                })
            
            orders_response.append(OrderResponse(
                id=order.id,
                user_id=order.user_id,
                total_amount=order.total_amount,
                status=order.status,
                payment_status=order.payment_status,
                payment_method=order.payment_method,
                shipping_address=order.shipping_address,
                billing_address=order.billing_address,
                created_at=order.created_at,
                updated_at=order.updated_at,
                items=items_response
            ))
        
        return orders_response
    except Exception as e:
        logger.error(f"Error listing orders: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing orders: {str(e)}"
        )

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_endpoint(
    order_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get order by ID"""
    try:
        order = get_order(db, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Users can only access their own orders
        if order.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        items_response = []
        for item in order_items:
            product = get_product(db, item.product_id)
            items_response.append({
                "id": item.id,
                "product_id": item.product_id,
                "product_name": product.name if product else "Unknown",
                "quantity": item.quantity,
                "price": item.price_at_time,
                "size": item.size,
                "color": item.color
            })
        
        return OrderResponse(
            id=order.id,
            user_id=order.user_id,
            total_amount=order.total_amount,
            status=order.status,
            payment_status=order.payment_status,
            payment_method=order.payment_method,
            shipping_address=order.shipping_address,
            billing_address=order.billing_address,
            created_at=order.created_at,
            updated_at=order.updated_at,
            items=items_response
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving order: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving order: {str(e)}"
        )

@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status_endpoint(
    order_id: str,
    status_update: OrderStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update order status"""
    try:
        order = get_order(db, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Users can only update their own orders (or admin)
        if order.user_id != current_user.id:
            # Check if user is admin (simplified check)
            if "admin" not in current_user.email.lower():
                raise HTTPException(status_code=403, detail="Not authorized")
        
        # Validate status
        valid_statuses = ["pending", "confirmed", "paid", "shipped", "delivered", "cancelled"]
        if status_update.status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        updated_order = update_order_status(db, order_id, status_update.status)
        if not updated_order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Update updated_at timestamp
        updated_order.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(updated_order)
        
        # Get order items for response
        order_items = db.query(OrderItem).filter(OrderItem.order_id == updated_order.id).all()
        items_response = []
        for item in order_items:
            product = get_product(db, item.product_id)
            items_response.append({
                "id": item.id,
                "product_id": item.product_id,
                "product_name": product.name if product else "Unknown",
                "quantity": item.quantity,
                "price": item.price_at_time,
                "size": item.size,
                "color": item.color
            })
        
        return OrderResponse(
            id=updated_order.id,
            user_id=updated_order.user_id,
            total_amount=updated_order.total_amount,
            status=updated_order.status,
            payment_status=updated_order.payment_status,
            payment_method=updated_order.payment_method,
            shipping_address=updated_order.shipping_address,
            billing_address=updated_order.billing_address,
            created_at=updated_order.created_at,
            updated_at=updated_order.updated_at,
            items=items_response
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating order status: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error updating order status: {str(e)}"
        )

@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cancel an order"""
    try:
        order = get_order(db, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        if order.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Only allow cancellation if order is pending or confirmed
        if order.status not in ["pending", "confirmed"]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel order with status: {order.status}"
            )
        
        # Restore inventory
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        for item in order_items:
            product = get_product(db, item.product_id)
            if product:
                product.stock_quantity += item.quantity
        
        # Update order status
        updated_order = update_order_status(db, order_id, "cancelled")
        updated_order.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(updated_order)
        
        # Get order items for response
        items_response = []
        for item in order_items:
            product = get_product(db, item.product_id)
            items_response.append({
                "id": item.id,
                "product_id": item.product_id,
                "product_name": product.name if product else "Unknown",
                "quantity": item.quantity,
                "price": item.price_at_time,
                "size": item.size,
                "color": item.color
            })
        
        return OrderResponse(
            id=updated_order.id,
            user_id=updated_order.user_id,
            total_amount=updated_order.total_amount,
            status=updated_order.status,
            payment_status=updated_order.payment_status,
            payment_method=updated_order.payment_method,
            shipping_address=updated_order.shipping_address,
            billing_address=updated_order.billing_address,
            created_at=updated_order.created_at,
            updated_at=updated_order.updated_at,
            items=items_response
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling order: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error cancelling order: {str(e)}"
        )

