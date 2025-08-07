from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    api_title: str = "Valorant Match Scraper API"
    api_version: str = "1.0.0"
    api_description: str = "API for scraping Valorant match data"
    
    # Scraping Settings
    base_url: str = "https://tracker.gg/valorant"
    request_timeout: int = 30
    max_retries: int = 3
    delay_between_requests: float = 1.0
    
    # Database Settings (if needed)
    database_url: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
