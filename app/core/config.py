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
        try:
            if isinstance(v, str):
                # Handle empty string
                if not v or v.strip() == "":
                    return ["*"]  # Allow all origins as fallback

                # Fix smart quotes to regular quotes
                v = (
                    v.replace('"', '"')
                    .replace('"', '"')
                    .replace("'", "'")
                    .replace("'", "'")
                    .replace("\\n", "")  # Remove newlines
                    .replace("\\r", "")  # Remove carriage returns
                    .strip()
                )

                # Handle JSON array format
                if v.startswith("["):
                    # Try to parse as JSON
                    try:
                        result = json.loads(v)
                        if isinstance(result, list):
                            return result
                    except json.JSONDecodeError:
                        # If JSON parsing fails, try to clean and split
                        v = v.strip("[]")
                        origins = []
                        for item in v.split(","):
                            cleaned = item.strip().strip('"').strip("'").strip()
                            if cleaned:
                                origins.append(cleaned)
                        return origins if origins else ["*"]
                else:
                    # Split by comma
                    origins = []
                    for item in v.split(","):
                        cleaned = item.strip()
                        if cleaned:
                            origins.append(cleaned)
                    return origins if origins else ["*"]
            elif isinstance(v, list):
                return v
            return ["*"]  # Allow all origins as fallback
        except Exception as e:
            print(f"Error parsing BACKEND_CORS_ORIGINS: {e}, using wildcard")
            return ["*"]  # Allow all origins on error

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
