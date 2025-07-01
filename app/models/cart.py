"""Shopping cart models."""

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Integer, ForeignKey, func
from datetime import datetime
from typing import List
from app.core.database import Base

class Cart(Base):
    __tablename__ = "carts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="cart")
    items: Mapped[List["CartItem"]] = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Cart(id={self.id}, user_id={self.user_id})>"

class CartItem(Base):
    __tablename__ = "cart_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    
    cart_id: Mapped[int] = mapped_column(Integer, ForeignKey("carts.id"))
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Relationships
    cart: Mapped["Cart"] = relationship("Cart", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="cart_items")
    
    def __repr__(self) -> str:
        return f"<CartItem(id={self.id}, product_id={self.product_id}, quantity={self.quantity})>"