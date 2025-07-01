"""Shopping cart service."""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from app.models.cart import Cart, CartItem
from app.models.product import Product
from typing import Optional, List

class CartService:
    """Service layer for shopping cart operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_cart(self, user_id: int) -> Cart:
        """Get user's cart or create if doesn't exist."""
        stmt = select(Cart).where(Cart.user_id == user_id)
        cart = self.db.execute(stmt).scalar_one_or_none()
        
        if not cart:
            cart = Cart(user_id=user_id)
            self.db.add(cart)
            self.db.commit()
            self.db.refresh(cart)
        
        return cart
    
    def get_cart_items(self, user_id: int) -> List[CartItem]:
        """Get all items in user's cart."""
        cart = self.get_or_create_cart(user_id)
        stmt = (select(CartItem)
                .options(joinedload(CartItem.product))
                .where(CartItem.cart_id == cart.id))
        result = self.db.execute(stmt)
        return result.scalars().all()
    
    def add_to_cart(self, user_id: int, product_id: int, quantity: int = 1) -> CartItem:
        """Add item to cart or update quantity if exists."""
        cart = self.get_or_create_cart(user_id)
        
        # Check if item already in cart
        stmt = select(CartItem).where(
            and_(CartItem.cart_id == cart.id, CartItem.product_id == product_id)
        )
        existing_item = self.db.execute(stmt).scalar_one_or_none()
        
        if existing_item:
            existing_item.quantity += quantity
            self.db.commit()
            self.db.refresh(existing_item)
            return existing_item
        else:
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity
            )
            self.db.add(cart_item)
            self.db.commit()
            self.db.refresh(cart_item)
            return cart_item
    
    def update_cart_item(self, user_id: int, product_id: int, quantity: int) -> Optional[CartItem]:
        """Update cart item quantity."""
        cart = self.get_or_create_cart(user_id)
        stmt = select(CartItem).where(
            and_(CartItem.cart_id == cart.id, CartItem.product_id == product_id)
        )
        cart_item = self.db.execute(stmt).scalar_one_or_none()
        
        if cart_item:
            if quantity <= 0:
                self.db.delete(cart_item)
            else:
                cart_item.quantity = quantity
            self.db.commit()
            return cart_item
        
        return None
    
    def remove_from_cart(self, user_id: int, product_id: int) -> bool:
        """Remove item from cart."""
        cart = self.get_or_create_cart(user_id)
        stmt = select(CartItem).where(
            and_(CartItem.cart_id == cart.id, CartItem.product_id == product_id)
        )
        cart_item = self.db.execute(stmt).scalar_one_or_none()
        
        if cart_item:
            self.db.delete(cart_item)
            self.db.commit()
            return True
        
        return False
    
    def clear_cart(self, user_id: int) -> bool:
        """Clear all items from cart."""
        cart = self.get_or_create_cart(user_id)
        stmt = select(CartItem).where(CartItem.cart_id == cart.id)
        cart_items = self.db.execute(stmt).scalars().all()
        
        for item in cart_items:
            self.db.delete(item)
        
        self.db.commit()
        return True
    
    def get_cart_total(self, user_id: int) -> float:
        """Calculate cart total."""
        cart_items = self.get_cart_items(user_id)
        total = sum(item.product.price * item.quantity for item in cart_items)
        return round(total, 2)
    
    def get_cart_count(self, user_id: int) -> int:
        """Get total number of items in cart."""
        cart_items = self.get_cart_items(user_id)
        return sum(item.quantity for item in cart_items)