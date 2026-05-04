from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
import os

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "AetherStore Engine"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # Infrastructure
    DATABASE_URL: str = "sqlite:///./aetherstore.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production-32-chars-at-least"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    CORS_ORIGINS: str = "*"
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: str = "*"
    CORS_HEADERS: str = "*"
    
    # Payments
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLIC_KEY: str = ""
    PAYSTACK_SECRET_KEY: str = ""
    PAYSTACK_PUBLIC_KEY: str = ""
    
    # Email
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    EMAIL_USERNAME: str = ""
    EMAIL_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@aetherstore.com"
    
    # AI Model Paths - 27 Pillars
    MODEL_PATH_CLIP: str = "backend/ai_models/openfashionclip.pt"
    MODEL_PATH_SHAPER: str = "backend/ai_models/shaper_weights.pt"
    MODEL_PATH_BOXER: str = "backend/ai_models/boxer_net.pt"
    MODEL_PATH_MOMENTUM: str = "backend/ai_models/momentum_solver.pt"
    MODEL_PATH_SAPIENS: str = "backend/ai_models/sapiens_1b.pt"
    MODEL_PATH_TRIBE: str = "backend/ai_models/tribev2_weights.pt"
    MODEL_PATH_MUSICGEN: str = "facebook/musicgen-small"
    MODEL_PATH_FLOWDEC: str = "backend/ai_models/flowdec_weights.pt"
    MODEL_PATH_MOVIEGEN: str = "facebook/movie-gen-video"
    MODEL_PATH_VJEPA: str = "facebook/vjepa-large"
    MODEL_PATH_LLAMA: str = "meta-llama/Llama-3-8B-Instruct"
    MODEL_PATH_LLAMA_VISION: str = "meta-llama/Llama-3.2-11B-Vision-Instruct"
    MODEL_PATH_DTC: str = "backend/ai_models/dtc_lrm.pt"
    MODEL_PATH_SAM2_VIDEO: str = "backend/ai_models/sam2_video.pt"
    MODEL_PATH_SAM3: str = "backend/ai_models/sam3_hq.pt"
    MODEL_PATH_MAVERICK: str = "meta-llama/Llama-4-400B-Maverick"
    MODEL_PATH_SPIRIT_LM: str = "facebook/spirit-lm-base"
    MODEL_PATH_SEAMLESS: str = "facebook/seamless-m4t-v2-large"
    MODEL_PATH_ANIMATION: str = "backend/ai_models/locomotion_net.pt"
    MODEL_PATH_SCENESCRIPT: str = "backend/ai_models/scenescript_v1.pt"
    MODEL_PATH_TACTOVIS: str = "backend/ai_models/tactovis_core.pt"
    MODEL_PATH_LOCATE3D: str = "backend/ai_models/locate3d_v1.pt"
    
    # Asset Directories
    UPLOAD_DIR: str = "backend/uploads"
    DATA_DIR: str = "backend/data"
    TEMP_DIR: str = "backend/temp"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()
