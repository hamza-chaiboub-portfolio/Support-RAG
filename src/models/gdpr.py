"""GDPR compliance models and utilities"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from helpers.database import Base
import enum
import json


class ConsentType(str, enum.Enum):
    """Types of user consent"""
    ANALYTICS = "analytics"
    MARKETING = "marketing"
    DATA_PROCESSING = "data_processing"
    COOKIES = "cookies"


class UserConsent(Base):
    """User consent tracking for GDPR compliance"""
    __tablename__ = "user_consents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    consent_type = Column(SQLEnum(ConsentType), nullable=False)
    given = Column(Boolean, default=False)
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserConsent(user_id={self.user_id}, type={self.consent_type}, given={self.given})>"


class DataExportRequest(Base):
    """Track GDPR data export requests"""
    __tablename__ = "data_export_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    request_type = Column(String(50), default="full")  # full, partial
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    file_path = Column(String(512), nullable=True)
    download_token = Column(String(255), unique=True, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<DataExportRequest(user_id={self.user_id}, status={self.status})>"


class DataDeletionRequest(Base):
    """Track GDPR data deletion requests"""
    __tablename__ = "data_deletion_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    reason = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    scheduled_at = Column(DateTime, nullable=True)  # 30-day grace period
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<DataDeletionRequest(user_id={self.user_id}, status={self.status})>"
