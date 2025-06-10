from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    PROJECT_NAME: str = "DOGEPAL - Spending Recommendation Engine"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    
    # Server settings
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # Debug mode
    DEBUG: bool = True
    
    # Database
    SQLALCHEMY_DATABASE_URI: str = "sqlite+aiosqlite:///./dogepal.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"  # Change in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Allow extra environment variables without validation
    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"  # Allow extra environment variables

settings = Settings()
