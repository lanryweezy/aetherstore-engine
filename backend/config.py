# config.py
# Configuration settings for Aetherstore Engine backend

import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Aetherstore Engine"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    SENTRY_DSN: Optional[str] = None
    
    # Database settings
    DATABASE_URL: str = "postgresql://localhost/aetherstore_dev"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    CORS_ORIGINS: str = "*"
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: str = "*"
    CORS_HEADERS: str = "*"
    
    # File storage settings
    UPLOAD_DIR: str = "uploads"
    TEMP_DIR: str = "temp"
    MAX_FILE_SIZE_MB: int = 50
    
    # AI service settings
    AI_SERVICE_URL: str = "http://localhost:8001"
    AI_MODEL_TIMEOUT_SECONDS: int = 300
    
    # 3D processing settings
    MAX_POLYGON_COUNT: int = 100000
    TEXTURE_RESOLUTION: str = "4k"
    
    # WebSocket settings for real-time features
    WEBSOCKET_HOST: str = "0.0.0.0"
    WEBSOCKET_PORT: int = 8002
    
    # Redis settings for caching and sessions
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_CACHE_TTL_SECONDS: int = 3600
    
    # Email settings
    EMAIL_PROVIDER: str = "sendgrid"  # "sendgrid", "mailgun", or "smtp"
    EMAIL_SENDGRID_API_KEY: str = ""
    EMAIL_MAILGUN_API_KEY: str = ""
    EMAIL_MAILGUN_DOMAIN: str = ""
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    EMAIL_USERNAME: str = ""
    EMAIL_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@aetherstore.engine"
    FROM_NAME: str = "Aetherstore Engine"
    
    # Payment settings
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLIC_KEY: str = ""
    PAYSTACK_SECRET_KEY: str = ""
    PAYSTACK_PUBLIC_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    PAYPAL_CLIENT_ID: str = ""
    PAYPAL_SECRET: str = ""
    
    # CDN settings
    CDN_BASE_URL: str = ""
    
    # Analytics settings
    ANALYTICS_BATCH_SIZE: int = 50
    ANALYTICS_FLUSH_INTERVAL_SECONDS: int = 30
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"
    
    # Security Hardening
    RATE_LIMIT_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()

# Environment-specific configurations
def get_environment_config():
    """Get environment-specific configuration"""
    configs = {
        "development": {
            "DEBUG": True,
            "LOG_LEVEL": "DEBUG",
            "DATABASE_URL": "postgresql://localhost/aetherstore_dev"
        },
        "staging": {
            "DEBUG": False,
            "LOG_LEVEL": "INFO",
            "DATABASE_URL": os.getenv("STAGING_DATABASE_URL", "postgresql://localhost/aetherstore_staging")
        },
        "production": {
            "DEBUG": False,
            "LOG_LEVEL": "WARNING",
            "DATABASE_URL": os.getenv("PRODUCTION_DATABASE_URL", "postgresql://localhost/aetherstore_prod")
        }
    }
    
    return configs.get(settings.ENVIRONMENT, configs["development"])