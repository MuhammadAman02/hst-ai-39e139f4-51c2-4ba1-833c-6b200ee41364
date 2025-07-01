"""Order service for order management."""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from app.models.order import Order, OrderItem, OrderStatus
from app.models.cart import CartItem
from app.core.config import settings
from typing import Optional, List
import uuid
from datetime import datetime

class OrderService:
    """Service layer for order operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_order_from_cart(self, user_id: int, cart_items: List[CartItem], 
                              shipping_info: dict) -> Order:
        """Create order from cart items."""
        # Calculate totals
        subtotal = sum(item.product.price * item.quantity for item in cart_items)
        tax_amount = round(subtotal * settings.tax_rate, 2)
        
        # Calculate shipping
        shipping_cost = 0.0 if subtotal >= settings.free_shipping_threshold else settings.shipping_cost
        
        total_amount = round(subtotal + tax_amount + shipping_cost, 2)
        
        # Generate order number
        order_number = f"VER-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Create order
        order = Order(
            order_number=order_number,
            user_id=user_id,
            subtotal=subtotal,
            tax_amount=tax_amount,
            shipping_cost=shipping_cost,
            total_amount=total_amount,
            shipping_name=shipping_info['name'],
            shipping_address=shipping_info['address'],
            shipping_phone=shipping_info.get('phone'),
            payment_method=shipping_info.get('payment_method', 'Credit Card'),
            status=OrderStatus.PENDING
        )
        
        self.db.add(order)
        self.db.flush()  # Get order ID
        
        # Create order items
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            self.db.add(order_item)
        
        self.db.commit()
        self.db.refresh(order)
        return order
    
    def get_order(self, order_id: int) -> Optional[Order]:
        """Get order by ID with items loaded."""
        stmt = (select(Order)
                .options(joinedload(Order.items).joinedload(OrderItem.product))
                .where(Order.id == order_id))
        return self.db.execute(stmt).scalar_one_or_none()
    
    def get_user_orders(self, user_id: int) -> List[Order]:
        """Get all orders for a user."""
        stmt = (select(Order)
                .options(joinedload(Order.items).joinedload(OrderItem.product))
                .where(Order.user_id == user_id)
                .order_by(Order.created_at.desc()))
        result = self.db.execute(stmt)
        return result.scalars().all()
    
    def get_all_orders(self) -> List[Order]:
        """Get all orders (admin function)."""
        stmt = (select(Order)
                .options(joinedload(Order.user), joinedload(Order.items).joinedload(OrderItem.product))
                .order_by(Order.created_at.desc()))
        result = self.db.execute(stmt)
        return result.scalars().all()
    
    def update_order_status(self, order_id: int, status: OrderStatus) -> Optional[Order]:
        """Update order status."""
        order = self.get_order(order_id)
        if order:
            order.status = status
            self.db.commit()
            self.db.refresh(order)
        return order
    
    def cancel_order(self, order_id: int) -> Optional[Order]:
        """Cancel an order."""
        return self.update_order_status(order_id, OrderStatus.CANCELLED)