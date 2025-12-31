"""User model with proper authentication"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from helpers.database import Base
import enum


class UserRole(str, enum.Enum):
    """User roles for RBAC"""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


class User(Base):
    """User model with password hashing"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"
