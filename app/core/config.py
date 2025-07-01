"""Application configuration using pydantic-settings V2."""

from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from typing import Optional

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = Field(default="Versace Perfume Store")
    debug: bool = Field(default=True)
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8080)
    
    # Database
    database_url: str = Field(default="sqlite:///./data/versace_store.db")
    
    # Security
    secret_key: str = Field(default="versace-luxury-perfume-store-secret-key-2025")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=1440)  # 24 hours
    
    # File uploads
    max_file_size: int = Field(default=5 * 1024 * 1024)  # 5MB
    upload_directory: str = Field(default="./app/static/uploads")
    
    # Store settings
    currency: str = Field(default="USD")
    tax_rate: float = Field(default=0.08)  # 8% tax
    shipping_cost: float = Field(default=9.99)
    free_shipping_threshold: float = Field(default=75.00)

settings = Settings()