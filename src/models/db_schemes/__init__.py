"""Database schemas for RAG application"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Asset(BaseModel):
    """Asset database model"""
    asset_project_id: int
    asset_type: str
    asset_name: str
    asset_size: int
    asset_id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DataChunk(BaseModel):
    """Data chunk database model"""
    chunk_id: Optional[int] = None
    asset_id: int
    chunk_content: str
    chunk_index: int
    embedding: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True