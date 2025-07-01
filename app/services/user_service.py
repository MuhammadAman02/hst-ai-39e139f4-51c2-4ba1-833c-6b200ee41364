"""User service for authentication and user management."""

from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User
from app.core.auth import AuthManager
from typing import Optional

class UserService:
    """Service layer for user operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.get(User, user_id)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        stmt = select(User).where(User.email == email)
        return self.db.execute(stmt).scalar_one_or_none()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        stmt = select(User).where(User.username == username)
        return self.db.execute(stmt).scalar_one_or_none()
    
    def create_user(self, user_data: dict) -> User:
        """Create new user."""
        hashed_password = AuthManager.get_password_hash(user_data['password'])
        db_user = User(
            email=user_data['email'],
            username=user_data['username'],
            hashed_password=hashed_password,
            full_name=user_data.get('full_name'),
            phone=user_data.get('phone'),
            address=user_data.get('address')
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user credentials."""
        user = self.get_user_by_email(email)
        if not user or not AuthManager.verify_password(password, user.hashed_password):
            return None
        return user
    
    def update_user(self, user_id: int, user_data: dict) -> Optional[User]:
        """Update user information."""
        db_user = self.get_user(user_id)
        if not db_user:
            return None
        
        for field, value in user_data.items():
            if hasattr(db_user, field) and value is not None:
                setattr(db_user, field, value)
        
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def create_admin_user(self):
        """Create default admin user if it doesn't exist."""
        admin_email = "admin@versace.com"
        existing_admin = self.get_user_by_email(admin_email)
        
        if not existing_admin:
            admin_data = {
                'email': admin_email,
                'username': 'admin',
                'password': 'admin123',  # Change this in production!
                'full_name': 'Store Administrator'
            }
            admin_user = self.create_user(admin_data)
            admin_user.is_admin = True
            self.db.commit()
            return admin_user
        
        return existing_admin