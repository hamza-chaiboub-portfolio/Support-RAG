"""User controller for authentication and user management"""

from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from helpers.password import hash_password, verify_password
from helpers.logger import logger
from models.user import User, UserRole


class UserController:
    """Handle user-related operations"""
    
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> User:
        """Get user by username"""
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        return result.scalar()
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
        """Get user by ID"""
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar()
    
    @staticmethod
    async def create_user(
        db: AsyncSession,
        username: str,
        email: str,
        password: str,
        role: UserRole = UserRole.USER
    ) -> User:
        """Create a new user with hashed password"""
        hashed_pwd = hash_password(password)
        
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_pwd,
            role=role
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"User created: {username} with role {role.value}")
        return user
    
    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        username: str,
        password: str
    ) -> User:
        """Authenticate user by username and password"""
        user = await UserController.get_user_by_username(db, username)
        
        if not user:
            logger.warning(f"Login attempt for non-existent user: {username}")
            return None
        
        if not user.is_active:
            logger.warning(f"Login attempt for inactive user: {username}")
            return None
        
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Failed login for user: {username}")
            return None
        
        # Update last login
        stmt = update(User).where(User.id == user.id).values(last_login=datetime.utcnow())
        await db.execute(stmt)
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"Successful login: {username}")
        return user
    
    @staticmethod
    async def change_password(
        db: AsyncSession,
        user_id: int,
        old_password: str,
        new_password: str
    ) -> bool:
        """Change user password"""
        user = await UserController.get_user_by_id(db, user_id)
        
        if not user:
            return False
        
        if not verify_password(old_password, user.hashed_password):
            logger.warning(f"Password change failed - invalid old password for user: {user.username}")
            return False
        
        hashed_new = hash_password(new_password)
        stmt = update(User).where(User.id == user_id).values(hashed_password=hashed_new)
        await db.execute(stmt)
        await db.commit()
        
        logger.info(f"Password changed for user: {user.username}")
        return True
