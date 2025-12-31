"""Secure secrets management using environment variables and vault patterns"""

import os
from functools import lru_cache
from helpers.logger import logger


class SecretsManager:
    """
    Secure secrets management.
    
    Security Best Practices:
    - Secrets loaded from environment variables only
    - Never hardcode secrets
    - Use strong defaults
    - Validate secret availability at startup
    """
    
    # Required secrets - must be set in environment
    REQUIRED_SECRETS = [
        "JWT_SECRET_KEY",
        "DATABASE_URL",
        "LLM_API_KEY" if os.getenv("LLM_PROVIDER") != "mock" else None,
    ]
    
    @staticmethod
    @lru_cache(maxsize=1)
    def get_jwt_secret() -> str:
        """Get JWT secret key from environment"""
        secret = os.getenv("JWT_SECRET_KEY")
        if not secret or len(secret) < 32:
            logger.error("JWT_SECRET_KEY not set or too short (min 32 chars)")
            raise ValueError("Invalid JWT_SECRET_KEY")
        return secret
    
    @staticmethod
    def get_database_url() -> str:
        """Get database connection URL from environment"""
        url = os.getenv("DATABASE_URL")
        if not url:
            logger.error("DATABASE_URL not set")
            raise ValueError("DATABASE_URL not configured")
        
        if "localhost" in url and os.getenv("ENV") == "production":
            logger.error("Localhost database URL detected in production")
            raise ValueError("Invalid database configuration for production")
        
        return url
    
    @staticmethod
    def get_llm_api_key() -> str:
        """Get LLM provider API key from environment"""
        provider = os.getenv("LLM_PROVIDER", "mock")
        
        if provider == "mock":
            return "mock-key"
        
        api_key = os.getenv("LLM_API_KEY")
        if not api_key:
            logger.error(f"LLM_API_KEY not set for provider: {provider}")
            raise ValueError(f"LLM_API_KEY required for {provider}")
        
        return api_key
    
    @staticmethod
    def validate_secrets() -> None:
        """Validate all required secrets are available and secure. Raises ValueError if validation fails."""
        missing = []
        
        required = [s for s in SecretsManager.REQUIRED_SECRETS if s]
        
        # Add ENCRYPTION_KEY to required if production
        is_production = os.getenv("ENV") == "production"
        if is_production:
            required.append("ENCRYPTION_KEY")
        
        for secret_name in required:
            if not os.getenv(secret_name):
                missing.append(secret_name)
        
        if missing:
            error_msg = f"Missing required secrets: {', '.join(missing)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        # Production security checks
        if is_production:
            weak_keys = ["secret", "password", "changeme", "default", "123456", "qwerty"]
            
            # Check JWT Secret
            jwt_secret = os.getenv("JWT_SECRET_KEY", "")
            if len(jwt_secret) < 32:
                error_msg = "JWT_SECRET_KEY is too short for production (min 32 chars)"
                logger.error(error_msg)
                raise ValueError(error_msg)
            if any(weak in jwt_secret.lower() for weak in weak_keys):
                error_msg = "JWT_SECRET_KEY contains weak/default values"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            # Check Encryption Key
            enc_key = os.getenv("ENCRYPTION_KEY", "")
            if len(enc_key) < 32:
                error_msg = "ENCRYPTION_KEY is too short for production (min 32 chars)"
                logger.error(error_msg)
                raise ValueError(error_msg)
            if any(weak in enc_key.lower() for weak in weak_keys):
                error_msg = "ENCRYPTION_KEY contains weak/default values"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            # Check Database URL
            db_url = os.getenv("DATABASE_URL", "")
            if "localhost" in db_url or "127.0.0.1" in db_url:
                error_msg = "Localhost database URL detected in production"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            # Check CORS Origins
            cors_origins_str = os.getenv("BACKEND_CORS_ORIGINS", "")
            if not cors_origins_str:
                error_msg = "BACKEND_CORS_ORIGINS not configured for production"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            try:
                import json
                cors_origins = json.loads(cors_origins_str) if cors_origins_str.startswith("[") else [cors_origins_str]
            except (json.JSONDecodeError, TypeError):
                cors_origins = [cors_origins_str]
            
            if "*" in cors_origins:
                error_msg = "Wildcard CORS origin (*) is not allowed in production"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            for origin in cors_origins:
                if "localhost" in origin or "127.0.0.1" in origin:
                    error_msg = f"Localhost CORS origin ({origin}) is not allowed in production"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                if not origin.startswith(("http://", "https://")):
                    error_msg = f"CORS origin must use http or https protocol: {origin}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
            
            # Check Allowed Hosts
            allowed_hosts_str = os.getenv("ALLOWED_HOSTS", "")
            if allowed_hosts_str:
                try:
                    allowed_hosts = json.loads(allowed_hosts_str) if allowed_hosts_str.startswith("[") else allowed_hosts_str.split(",")
                except (json.JSONDecodeError, TypeError):
                    allowed_hosts = [allowed_hosts_str]
                
                for host in allowed_hosts:
                    if host in ("localhost", "127.0.0.1", "*"):
                        error_msg = f"Localhost/wildcard not allowed in ALLOWED_HOSTS for production: {host}"
                        logger.error(error_msg)
                        raise ValueError(error_msg)
        
        logger.info("All required secrets validated successfully")
        return None
    
    @staticmethod
    def mask_secret(secret: str, visible_chars: int = 4) -> str:
        """
        Mask a secret for logging purposes.
        Only shows first and last N characters.
        """
        if len(secret) <= visible_chars * 2:
            return "*" * len(secret)
        return secret[:visible_chars] + "*" * (len(secret) - visible_chars * 2) + secret[-visible_chars:]
