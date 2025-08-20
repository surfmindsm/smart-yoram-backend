from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator
import json


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

    BACKEND_CORS_ORIGINS: List[str] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("["):
                # Try to parse as JSON
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    # If JSON parsing fails, split by comma
                    return [i.strip() for i in v.split(",")]
            else:
                # Split by comma
                return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return []

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
