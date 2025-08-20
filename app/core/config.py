from typing import List, Union, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator, Field
import json
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart Yoram API"
    VERSION: str = "1.1.0"
    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    DATABASE_URL: str

    # Supabase settings
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str

    # CORS settings - completely optional with safe defaults
    BACKEND_CORS_ORIGINS: Optional[Union[List[str], str]] = Field(
        default=["*"],  # Allow all origins by default
        description="List of allowed CORS origins"
    )

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Optional[Union[str, List[str]]]) -> List[str]:
        # If nothing provided, use default
        if v is None:
            return ["*"]
        
        # If already a list, return it
        if isinstance(v, list):
            return v if v else ["*"]
        
        # If string, try simple comma-separated parsing
        if isinstance(v, str):
            # Handle empty or whitespace-only string
            v = v.strip()
            if not v:
                return ["*"]
            
            # Simple comma-separated parsing (no JSON)
            # This avoids all the JSON parsing issues
            origins = []
            for origin in v.split(","):
                cleaned = origin.strip()
                if cleaned:
                    # Remove any quotes
                    cleaned = cleaned.strip('"').strip("'")
                    if cleaned:
                        origins.append(cleaned)
            
            return origins if origins else ["*"]
        
        # Fallback to wildcard
        return ["*"]

    FIRST_SUPERUSER: str = "admin@smartyoram.com"
    FIRST_SUPERUSER_PASSWORD: str = "changeme"

    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"

    # Firebase Configuration
    FIREBASE_CREDENTIALS_PATH: str = "firebase-credentials.json"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env


settings = Settings()
