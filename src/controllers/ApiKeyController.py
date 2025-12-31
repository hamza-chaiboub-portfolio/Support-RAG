import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from models.api_key import ApiKey
from helpers.logger import logger

class ApiKeyController:
    """Controller for API Key management"""
    
    @staticmethod
    def _hash_key(key: str) -> str:
        """Hash API key for storage"""
        return hashlib.sha256(key.encode()).hexdigest()
    
    @staticmethod
    def generate_key() -> str:
        """Generate a secure random API key"""
        return f"sk_{secrets.token_urlsafe(32)}"
    
    @classmethod
    async def create_api_key(
        cls,
        db: AsyncSession,
        user_id: int,
        name: str,
        expires_in_days: Optional[int] = None
    ) -> Tuple[ApiKey, str]:
        """
        Create a new API key
        
        Returns:
            Tuple of (ApiKey object, raw_key_string)
        """
        raw_key = cls.generate_key()
        key_hash = cls._hash_key(raw_key)
        
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
            
        api_key = ApiKey(
            user_id=user_id,
            name=name,
            key_hash=key_hash,
            expires_at=expires_at
        )
        
        db.add(api_key)
        await db.commit()
        await db.refresh(api_key)
        
        logger.info(f"API Key created for user {user_id}: {name}")
        return api_key, raw_key

    @classmethod
    async def verify_api_key(cls, db: AsyncSession, raw_key: str) -> Optional[ApiKey]:
        """
        Verify an API key and update usage stats
        """
        key_hash = cls._hash_key(raw_key)
        
        stmt = select(ApiKey).where(
            ApiKey.key_hash == key_hash,
            ApiKey.is_active == True
        )
        result = await db.execute(stmt)
        api_key = result.scalar()
        
        if not api_key:
            return None
            
        if api_key.expires_at and api_key.expires_at < datetime.utcnow():
            return None
            
        # Update last used asynchronously (fire and forget ideally, but here we await)
        api_key.last_used_at = datetime.utcnow()
        await db.commit()
        
        return api_key

    @staticmethod
    async def list_keys(db: AsyncSession, user_id: int):
        """List API keys for a user"""
        stmt = select(ApiKey).where(ApiKey.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def revoke_key(db: AsyncSession, key_id: int, user_id: int) -> bool:
        """Revoke (delete) an API key"""
        stmt = select(ApiKey).where(ApiKey.id == key_id, ApiKey.user_id == user_id)
        result = await db.execute(stmt)
        api_key = result.scalar()
        
        if not api_key:
            return False
            
        await db.delete(api_key)
        await db.commit()
        return True
