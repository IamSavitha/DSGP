"""
Configuration settings for the Kayak Simulation backend services.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Kayak Simulation"
    DEBUG: bool = True
    
    # MySQL Configuration
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_DATABASE: str = "kayak_db"
    MYSQL_USER: str = "kayak_user"
    MYSQL_PASSWORD: str = "kayak_pass"
    
    @property
    def MYSQL_URL(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
    
    # MongoDB Configuration
    MONGODB_URI: str = "mongodb://admin:kayak_mongo_pass@localhost:27017"
    MONGODB_DATABASE: str = "kayak_db"
    
    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    CACHE_TTL: int = 3600  # 1 hour default
    
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:29092"
    KAFKA_GROUP_ID: str = "kayak_consumer_group"
    
    # JWT Configuration
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Service URLs
    USER_SERVICE_URL: str = "http://localhost:8001"
    FLIGHT_SERVICE_URL: str = "http://localhost:8002"
    HOTEL_SERVICE_URL: str = "http://localhost:8003"
    CAR_SERVICE_URL: str = "http://localhost:8004"
    BILLING_SERVICE_URL: str = "http://localhost:8005"
    ADMIN_SERVICE_URL: str = "http://localhost:8006"
    SEARCH_SERVICE_URL: str = "http://localhost:8007"
    AI_SERVICE_URL: str = "http://localhost:8008"
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()

