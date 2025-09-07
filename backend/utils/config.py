from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Backend Configuration
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    BACKEND_WORKERS: int = 1
    BACKEND_RELOAD: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./infotainment_a11y.db"
    REDIS_URL: str = "redis://localhost:6379"
    
    # File Upload
    MAX_FILE_SIZE: int = 52428800  # 50MB in bytes
    UPLOAD_DIR: str = "./uploads"
    SANDBOX_DIR: str = "./sandbox"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # LLM Configuration
    LLM_PROVIDER: str = "none"  # none, openai, anthropic, deepseek
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_MODEL: str = "deepseek-coder"
    
    # Analysis Configuration
    MAX_CONCURRENT_AGENTS: int = 10
    ANALYSIS_TIMEOUT: int = 1800
    ENABLE_SANDBOX: bool = True
    AUTO_APPLY_PATCHES: bool = False
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get application settings"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

def reload_settings():
    """Reload settings from environment"""
    global _settings
    _settings = Settings()
    return _settings
