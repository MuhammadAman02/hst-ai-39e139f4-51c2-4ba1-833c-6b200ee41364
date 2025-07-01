"""SQLAlchemy V2 database setup with proper session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session
from app.core.config import settings
from app.core.logging import app_logger
import os

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Create engine with proper configuration
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=300
)

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass

def create_tables():
    """Create all database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        app_logger.info("Database tables created successfully")
    except Exception as e:
        app_logger.error(f"Error creating database tables: {e}")
        raise

def get_db() -> Session:
    """Database session dependency."""
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()

def init_sample_data():
    """Initialize sample data for the store."""
    from app.services.product_service import ProductService
    from app.services.category_service import CategoryService
    
    with Session(engine) as db:
        try:
            category_service = CategoryService(db)
            product_service = ProductService(db)
            
            # Check if data already exists
            if category_service.get_categories():
                app_logger.info("Sample data already exists, skipping initialization")
                return
            
            # Create categories
            categories_data = [
                {
                    "name": "Men's Fragrances",
                    "description": "Sophisticated and bold fragrances for the modern man",
                    "image_url": "/static/images/categories/mens.jpg"
                },
                {
                    "name": "Women's Fragrances", 
                    "description": "Elegant and captivating scents for the confident woman",
                    "image_url": "/static/images/categories/womens.jpg"
                },
                {
                    "name": "Unisex Collection",
                    "description": "Versatile fragrances that transcend gender boundaries",
                    "image_url": "/static/images/categories/unisex.jpg"
                }
            ]
            
            created_categories = []
            for cat_data in categories_data:
                category = category_service.create_category(cat_data)
                created_categories.append(category)
                app_logger.info(f"Created category: {category.name}")
            
            # Create sample products
            products_data = [
                {
                    "name": "Versace Eros",
                    "description": "A fragrance that interprets the sublime masculine through a luminous aura with an intense, vibrant, and glowing combination of fresh mint leaves, Italian lemon zest, and green apple.",
                    "price": 89.99,
                    "category_id": created_categories[0].id,  # Men's
                    "image_url": "/static/images/products/eros.jpg",
                    "stock_quantity": 50,
                    "size": "100ml"
                },
                {
                    "name": "Versace Bright Crystal",
                    "description": "A precious jewel of rare beauty characterized by a fresh, vibrant, flowery scent. An enthralling and voluptuous fragrance, for the Versace woman who is strong and confident.",
                    "price": 79.99,
                    "category_id": created_categories[1].id,  # Women's
                    "image_url": "/static/images/products/bright_crystal.jpg",
                    "stock_quantity": 45,
                    "size": "90ml"
                },
                {
                    "name": "Versace Dylan Blue",
                    "description": "An olfactory expression of strength and individuality. Fresh aquatic notes blend with modern woody essences in this contemporary masculine fragrance.",
                    "price": 94.99,
                    "category_id": created_categories[0].id,  # Men's
                    "image_url": "/static/images/products/dylan_blue.jpg",
                    "stock_quantity": 35,
                    "size": "100ml"
                },
                {
                    "name": "Versace Crystal Noir",
                    "description": "A magical fragrance, ethereal yet carnal, that makes a statement of iconic femininity and uncompromising glamour.",
                    "price": 85.99,
                    "category_id": created_categories[1].id,  # Women's
                    "image_url": "/static/images/products/crystal_noir.jpg",
                    "stock_quantity": 40,
                    "size": "90ml"
                },
                {
                    "name": "Versace Pour Homme",
                    "description": "The essence of the Versace man. A fragrance with Mediterranean accents, the heart of Versace Pour Homme is characterized by mineral-floral tones.",
                    "price": 69.99,
                    "category_id": created_categories[0].id,  # Men's
                    "image_url": "/static/images/products/pour_homme.jpg",
                    "stock_quantity": 60,
                    "size": "100ml"
                },
                {
                    "name": "Versace Versense",
                    "description": "A fresh fragrance that celebrates the woman in harmony with nature. Mediterranean essences blend with modern woody notes.",
                    "price": 74.99,
                    "category_id": created_categories[1].id,  # Women's
                    "image_url": "/static/images/products/versense.jpg",
                    "stock_quantity": 55,
                    "size": "100ml"
                }
            ]
            
            for product_data in products_data:
                product = product_service.create_product(product_data)
                app_logger.info(f"Created product: {product.name}")
            
            app_logger.info("Sample data initialization completed successfully")
            
        except Exception as e:
            app_logger.error(f"Error initializing sample data: {e}")
            db.rollback()
            raise