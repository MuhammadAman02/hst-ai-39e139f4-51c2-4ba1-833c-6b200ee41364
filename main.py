"""
Versace Perfume E-commerce Store
Luxury perfume shopping experience with elegant UI and complete e-commerce functionality.
"""

import asyncio
from nicegui import ui, app
from app.core.config import settings
from app.core.database import create_tables, init_sample_data
from app.core.logging import app_logger
from app.frontend.pages import home, products, cart, checkout, admin, auth
from app.core.auth import AuthManager

def setup_app():
    """Initialize the application with all necessary components."""
    try:
        # Create database tables
        create_tables()
        app_logger.info("Database tables created successfully")
        
        # Initialize sample data
        init_sample_data()
        app_logger.info("Sample data initialized")
        
        # Setup authentication
        AuthManager.setup()
        app_logger.info("Authentication system initialized")
        
        # Setup static files
        app.add_static_files('/static', 'app/static')
        app_logger.info("Static files configured")
        
    except Exception as e:
        app_logger.error(f"Error during app setup: {e}")
        raise

def main():
    """Main application entry point."""
    try:
        setup_app()
        
        # Set app title and favicon
        ui.page_title = "Versace Perfumes - Luxury Fragrances"
        
        app_logger.info(f"Starting {settings.app_name} on port {settings.port}")
        ui.run(
            title="Versace Perfumes",
            port=settings.port,
            host=settings.host,
            reload=settings.debug,
            show=settings.debug,
            favicon="🌟"
        )
        
    except Exception as e:
        app_logger.error(f"Failed to start application: {e}")
        raise

if __name__ in {"__main__", "__mp_main__"}:
    main()