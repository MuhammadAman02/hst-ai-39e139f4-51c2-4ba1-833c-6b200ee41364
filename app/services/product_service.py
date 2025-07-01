"""Product service for product management."""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, and_
from app.models.product import Product, Category, Review
from typing import Optional, List

class ProductService:
    """Service layer for product operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_product(self, product_id: int) -> Optional[Product]:
        """Get product by ID with category loaded."""
        stmt = select(Product).options(joinedload(Product.category)).where(Product.id == product_id)
        return self.db.execute(stmt).scalar_one_or_none()
    
    def get_products(self, category_id: Optional[int] = None, search: Optional[str] = None, 
                    limit: int = 50, offset: int = 0) -> List[Product]:
        """Get products with optional filtering."""
        stmt = select(Product).options(joinedload(Product.category)).where(Product.is_active == True)
        
        if category_id:
            stmt = stmt.where(Product.category_id == category_id)
        
        if search:
            search_term = f"%{search}%"
            stmt = stmt.where(Product.name.ilike(search_term))
        
        stmt = stmt.offset(offset).limit(limit)
        result = self.db.execute(stmt)
        return result.scalars().all()
    
    def get_featured_products(self, limit: int = 6) -> List[Product]:
        """Get featured products (newest products for demo)."""
        stmt = (select(Product)
                .options(joinedload(Product.category))
                .where(Product.is_active == True)
                .order_by(Product.created_at.desc())
                .limit(limit))
        result = self.db.execute(stmt)
        return result.scalars().all()
    
    def create_product(self, product_data: dict) -> Product:
        """Create new product."""
        db_product = Product(**product_data)
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product
    
    def update_product(self, product_id: int, product_data: dict) -> Optional[Product]:
        """Update product."""
        db_product = self.get_product(product_id)
        if not db_product:
            return None
        
        for field, value in product_data.items():
            if hasattr(db_product, field) and value is not None:
                setattr(db_product, field, value)
        
        self.db.commit()
        self.db.refresh(db_product)
        return db_product
    
    def delete_product(self, product_id: int) -> bool:
        """Soft delete product."""
        db_product = self.get_product(product_id)
        if not db_product:
            return False
        
        db_product.is_active = False
        self.db.commit()
        return True
    
    def get_product_reviews(self, product_id: int) -> List[Review]:
        """Get reviews for a product."""
        stmt = (select(Review)
                .options(joinedload(Review.user))
                .where(Review.product_id == product_id)
                .order_by(Review.created_at.desc()))
        result = self.db.execute(stmt)
        return result.scalars().all()
    
    def add_review(self, product_id: int, user_id: int, rating: int, comment: str) -> Review:
        """Add a review for a product."""
        review = Review(
            product_id=product_id,
            user_id=user_id,
            rating=rating,
            comment=comment
        )
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review