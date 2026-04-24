from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List, Literal

class Settings(BaseSettings):
    # Supabase configuration
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    
    # Anthropic configuration
    ANTHROPIC_API_KEY: str
    
    # Security configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Environment
    ENVIRONMENT: Literal["development", "production"] = "development"
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"] # Default to all, but can be overridden in .env

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
