import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "Multi-Agent Task Solver"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Orchestrator
    max_concurrent_agents: int = 5
    agent_timeout: int = 300  # seconds
    retry_attempts: int = 3
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Redis (for future use)
    redis_url: Optional[str] = None
    
    # Security
    cors_origins: list = ["*"]
    api_key_header: str = "X-API-Key"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get application settings"""
    return settings

