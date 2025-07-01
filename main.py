import os
import sys
from dotenv import load_dotenv
from nicegui import ui

# Load environment variables from .env file (if present)
load_dotenv()

# Import the page definitions from app.main
# This ensures that the @ui.page decorators in app/main.py are executed
# and the routes are registered with NiceGUI before ui.run() is called.
try:
    import app.main  # noqa: F401 -> Ensure app.main is imported to register pages
except ImportError as e:
    print(f"Error importing app.main: {e}")
    print("Make sure the app directory is properly set up.")
    sys.exit(1)

# Create FastAPI app outside the if block so it can be imported by uvicorn
from fastapi import FastAPI, APIRouter
from app.core import (
    settings, 
    app_logger, 
    setup_middleware, 
    setup_routers, 
    validate_environment,
    setup_error_handlers,
    HealthCheck,
    is_healthy,
    setup_nicegui
)

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url=f"{settings.API_PREFIX}/docs" if settings.API_PREFIX else "/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc" if settings.API_PREFIX else "/redoc",
)

# Set up error handlers
setup_error_handlers(app)

# Set up middleware
setup_middleware(app)

# Set up routers
setup_routers(app, api_prefix=settings.API_PREFIX)

# Validate environment
errors = validate_environment()
if errors:
    for error in errors:
        app_logger.error(f"Environment validation error: {error}")

# Optional: Set up database if configured
try:
    from app.core import setup_database
    setup_database()
except (ImportError, AttributeError):
    app_logger.info("Database not configured, skipping setup")



if __name__ in {"__main__", "__mp_main__"}: # Recommended by NiceGUI for multiprocessing compatibility
    try:
        # Setup NiceGUI integration with FastAPI
        from app.core.nicegui_setup import setup_nicegui
        setup_nicegui(app)
        
        # Run the application
        app_logger.info(f"Starting server at {settings.HOST}:{settings.PORT}")
        ui.run(
            host=settings.HOST,
            port=settings.PORT,
            title=settings.APP_NAME,
            uvicorn_logging_level='info' if settings.DEBUG else 'warning',
            reload=settings.DEBUG,  # IMPORTANT: Set to False for production/deployment
            storage_secret=settings.SECRET_KEY,  # Use the same secret key for session storage
        )
    except Exception as e:
        # Import traceback here to avoid circular imports
        import traceback
        
        # Try to use app_logger if available, otherwise fall back to print
        try:
            app_logger.critical(f"Error starting application: {e}")
            app_logger.critical(traceback.format_exc())
        except NameError:
            print(f"CRITICAL ERROR: {e}")
            print(traceback.format_exc())
        
        sys.exit(1)