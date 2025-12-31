from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from helpers.database import Base

class ApiKey(Base):
    """API Key model for external access"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key_hash = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", backref="api_keys")
    
    def __repr__(self):
        return f"<ApiKey(name={self.name}, user_id={self.user_id})>"
