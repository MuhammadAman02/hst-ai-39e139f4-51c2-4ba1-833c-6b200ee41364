"""Logging configuration for the application."""

import logging
import sys
from pathlib import Path

# Create logs directory
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(logs_dir / "app.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

app_logger = logging.getLogger("versace_store")