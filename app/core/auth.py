"""Authentication and authorization system."""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from nicegui import ui, app
from app.core.config import settings
from app.core.logging import app_logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthManager:
    """Centralized authentication management."""
    
    @staticmethod
    def setup():
        """Setup authentication system."""
        app.storage.user.setdefault('authenticated', False)
        app.storage.user.setdefault('user_id', None)
        app.storage.user.setdefault('username', None)
        app.storage.user.setdefault('is_admin', False)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate password hash."""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def login_user(user_id: int, username: str, is_admin: bool = False):
        """Login user and set session."""
        app.storage.user['authenticated'] = True
        app.storage.user['user_id'] = user_id
        app.storage.user['username'] = username
        app.storage.user['is_admin'] = is_admin
        app_logger.info(f"User {username} logged in successfully")
    
    @staticmethod
    def logout_user():
        """Logout user and clear session."""
        username = app.storage.user.get('username', 'Unknown')
        app.storage.user['authenticated'] = False
        app.storage.user['user_id'] = None
        app.storage.user['username'] = None
        app.storage.user['is_admin'] = False
        app_logger.info(f"User {username} logged out")
    
    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is authenticated."""
        return app.storage.user.get('authenticated', False)
    
    @staticmethod
    def get_current_user_id() -> Optional[int]:
        """Get current user ID."""
        return app.storage.user.get('user_id')
    
    @staticmethod
    def get_current_username() -> Optional[str]:
        """Get current username."""
        return app.storage.user.get('username')
    
    @staticmethod
    def is_admin() -> bool:
        """Check if current user is admin."""
        return app.storage.user.get('is_admin', False)

def require_auth(func):
    """Decorator to require authentication."""
    def wrapper(*args, **kwargs):
        if not AuthManager.is_authenticated():
            ui.navigate.to('/login')
            return
        return func(*args, **kwargs)
    return wrapper

def require_admin(func):
    """Decorator to require admin privileges."""
    def wrapper(*args, **kwargs):
        if not AuthManager.is_authenticated() or not AuthManager.is_admin():
            ui.notify('Admin access required', type='negative')
            ui.navigate.to('/')
            return
        return func(*args, **kwargs)
    return wrapper