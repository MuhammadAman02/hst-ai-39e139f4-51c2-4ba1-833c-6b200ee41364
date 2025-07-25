"""Core module for the application.

This module contains core functionality for the application, including:
- Configuration management
- Logging
- Exception handling
- Security utilities
- Database utilities
- Health checks
- Deployment utilities

These components provide the foundation for the application and should be
imported and used by other modules as needed.
"""

# This directory contains modules for:
# - config.py: Application configuration and environment variables
# - logging.py: Logging setup and configuration
# - exceptions.py: Custom exception classes and error handling
# - middleware.py: ASGI middleware for request/response processing
# - security.py: Security-related utilities (CORS, authentication, etc.)
# - health.py: Health check utilities
# - utils.py: Utility functions
# - database.py: Database utilities
# - deployment.py: Deployment utilities
# - error_handlers.py: Error handling utilities

# Import core modules for easy access
from app.core.config import settings
from app.core.logging import app_logger, get_logger
from app.core.exceptions import (
    AppException,
    NotFoundError,
    ValidationError,
    DatabaseError,
    ConfigurationError,
    ExternalServiceError,
    RateLimitError
)
from app.core.error_handlers import setup_error_handlers, create_error_response, with_error_handling
from app.core.middleware import setup_middleware
from app.core.utils import setup_routers, validate_environment, import_string, get_project_root
from app.core.health import HealthCheck, is_healthy
from app.core.nicegui_setup import setup_nicegui



try:
    from app.core.deployment import DeploymentManager
except ImportError:
    # Deployment module might not be used in all applications
    pass

# Database is optional and might not be used in all applications
try:
    from app.core.database import setup_database
    # Uncomment when you need database functionality
    # from app.core.database import get_db, create_tables
except ImportError:
    # Database module might not be used in all applications
    pass

__all__ = [
    "settings",
    
    "app_logger",
    "get_logger",
    "AppException",
    "NotFoundError",
    "ValidationError",
    "DatabaseError",
    "ConfigurationError",
    "ExternalServiceError",
    "RateLimitError",
    "setup_error_handlers",
    "create_error_response",
    "with_error_handling",
    "setup_middleware",
    "setup_routers",
    "validate_environment",
    "import_string",
    "get_project_root",
    "HealthCheck",
    "is_healthy",
    "setup_nicegui",
    # Optional modules
    "DeploymentManager",
    "setup_database",
]