from pydantic_settings import BaseSettings
from pydantic import model_validator, field_validator
from pathlib import Path
from typing import List
import json
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file"""

    ENV: str = "development"
    APP_NAME: str = "FastAPI-JWT-App"
    APP_VERSION: str = "1.0"

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # Database Configuration
    # Note: @ in password should be URL-encoded as %40
    DATABASE_URL: str = "postgresql://postgres:postgres@127.0.0.1:5432/supportrag"
    SQLALCHEMY_ECHO: bool = False
    
    # File handling
    FILE_DEFAULT_CHUNK_SIZE: int = 1024 * 1024  # 1MB default
    
    # LLM Configuration
    LLM_PROVIDER: str = "mock"  # openai, cohere, or mock
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-3.5-turbo"  # for OpenAI
    LLM_BASE_URL: str = ""  # for custom providers like OpenRouter
    
    # Embedding Configuration
    EMBEDDING_MODEL: str = "sentence-transformers"  # sentence-transformers or openai
    VECTOR_STORE_DIR: str = "./chroma_data"

    # Rate Limiting
    RATE_LIMIT_DEFAULT: str = "100/hour"

    # Security - CORS Origins
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8000"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    ENCRYPTION_KEY: str

    @field_validator('BACKEND_CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from environment variable (JSON format) or use defaults"""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [v]
        return v

    @field_validator('ALLOWED_HOSTS', mode='before')
    @classmethod
    def parse_allowed_hosts(cls, v):
        """Parse allowed hosts from environment variable (JSON format) or use defaults"""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return v.split(',')
        return v

    @model_validator(mode='after')
    def validate_production_security(self) -> 'Settings':
        """Enforce security constraints in production environment"""
        if self.ENV == "production":
            errors = []
            
            # 1. Validate JWT Secret
            if len(self.JWT_SECRET_KEY) < 32:
                errors.append("JWT_SECRET_KEY must be at least 32 characters in production")
            
            weak_keys = ["secret", "password", "changeme", "default", "123456", "qwerty"]
            if any(weak in self.JWT_SECRET_KEY.lower() for weak in weak_keys):
                errors.append("JWT_SECRET_KEY contains weak/default values")

            # 2. Validate Encryption Key
            if not self.ENCRYPTION_KEY or len(self.ENCRYPTION_KEY) < 32:
                errors.append("ENCRYPTION_KEY must be at least 32 characters in production")
            
            if any(weak in self.ENCRYPTION_KEY.lower() for weak in weak_keys):
                errors.append("ENCRYPTION_KEY contains weak/default values")

            # 3. Validate Database URL
            if "localhost" in self.DATABASE_URL or "127.0.0.1" in self.DATABASE_URL:
                errors.append("Cannot use localhost database in production")

            # 4. Validate CORS Origins (strict production requirements)
            if not self.BACKEND_CORS_ORIGINS:
                errors.append("BACKEND_CORS_ORIGINS must be configured in production")
            elif "*" in self.BACKEND_CORS_ORIGINS:
                errors.append("Wildcard CORS origin (*) is not allowed in production")
            
            for origin in self.BACKEND_CORS_ORIGINS:
                if "localhost" in origin or "127.0.0.1" in origin:
                    errors.append(f"Localhost CORS origin ({origin}) is not allowed in production")
                if not origin.startswith(("http://", "https://")):
                    errors.append(f"CORS origin must use http or https protocol: {origin}")

            # 5. Validate Allowed Hosts
            for host in self.ALLOWED_HOSTS:
                if host in ("localhost", "127.0.0.1", "*"):
                    errors.append(f"Localhost/wildcard not allowed in ALLOWED_HOSTS for production: {host}")

            if errors:
                raise ValueError(f"Production environment configuration errors:\n  - " + "\n  - ".join(errors))

        return self

    class Config:
        # Load .env from the same directory as this file
        env_file = str(Path(__file__).parent.parent / ".env")
        env_file_encoding = 'utf-8'
        case_sensitive = True
        extra = 'ignore'  # Ignore extra fields from .env file

    def log_config(self) -> None:
        """Log current configuration state for debugging"""
        try:
            from helpers.logger import logger
        except ImportError:
            from src.helpers.logger import logger

        logger.info(f"Environment: {self.ENV}")
        logger.info(f"Database: {self.DATABASE_URL.split('@')[0] if '@' in self.DATABASE_URL else 'configured'}")
        logger.info(f"CORS Origins: {self.BACKEND_CORS_ORIGINS}")
        logger.info(f"Allowed Hosts: {self.ALLOWED_HOSTS}")


_settings_cache = None

def get_settings():
    """Dependency injection for settings with caching"""
    global _settings_cache
    if _settings_cache is None:
        _settings_cache = Settings()
        try:
            _settings_cache.log_config()
        except Exception as e:
            pass
    return _settings_cache