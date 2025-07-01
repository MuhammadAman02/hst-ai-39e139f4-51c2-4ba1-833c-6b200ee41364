"""Category service for category management."""

from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.product import Category
from typing import Optional, List

class CategoryService:
    """Service layer for category operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_category(self, category_id: int) -> Optional[Category]:
        """Get category by ID."""
        return self.db.get(Category, category_id)
    
    def get_categories(self) -> List[Category]:
        """Get all active categories."""
        stmt = select(Category).where(Category.is_active == True).order_by(Category.name)
        result = self.db.execute(stmt)
        return result.scalars().all()
    
    def create_category(self, category_data: dict) -> Category:
        """Create new category."""
        db_category = Category(**category_data)
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category
    
    def update_category(self, category_id: int, category_data: dict) -> Optional[Category]:
        """Update category."""
        db_category = self.get_category(category_id)
        if not db_category:
            return None
        
        for field, value in category_data.items():
            if hasattr(db_category, field) and value is not None:
                setattr(db_category, field, value)
        
        self.db.commit()
        self.db.refresh(db_category)
        return db_category