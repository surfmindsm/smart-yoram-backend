from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator
import json


class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart Yoram API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Supabase Database URL
    DATABASE_URL: str = "postgresql://postgres.adzhdsajdamrflvybhxq:YOUR_DB_PASSWORD@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

    # Supabase Settings
    SUPABASE_URL: str = "https://adzhdsajdamrflvybhxq.supabase.co"
    SUPABASE_ANON_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFkemhkc2FqZGFtcmZsdnliaHhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM4NDg5ODEsImV4cCI6MjA2OTQyNDk4MX0.pgn6M5_ihDFt3ojQmCoc3Qf8pc7LzRvQEIDT7g1nW3c"
    SUPABASE_SERVICE_KEY: str  # Add service role key for admin operations

    BACKEND_CORS_ORIGINS: List[str] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("["):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    return [i.strip() for i in v.split(",")]
            else:
                return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return []

    FIRST_SUPERUSER: str = "admin@smartyoram.com"
    FIRST_SUPERUSER_PASSWORD: str = "changeme"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
