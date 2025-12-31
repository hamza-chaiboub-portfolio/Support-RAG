"""Pydantic schemas for Asset-related requests and responses"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class AssetType(str, Enum):
    """Asset type options"""
    PDF = "pdf"
    TEXT = "text"
    MARKDOWN = "markdown"
    DOCUMENT = "document"


class AssetCreateRequest(BaseModel):
    """Schema for creating an asset"""
    project_id: int = Field(..., description="Project ID")
    asset_type: AssetType = Field(..., description="Type of asset")
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": 1,
                "asset_type": "pdf"
            }
        }


class AssetResponse(BaseModel):
    """Schema for asset response"""
    id: int
    project_id: int
    filename: str
    asset_type: str
    file_size: int
    file_path: str
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "project_id": 1,
                "filename": "document.pdf",
                "asset_type": "pdf",
                "file_size": 1024000,
                "file_path": "/data/projects/1/file.pdf",
                "created_at": "2024-01-15T10:30:00"
            }
        }


class FileUploadResponse(BaseModel):
    """Schema for file upload response"""
    file_id: str = Field(..., description="Unique file identifier")
    asset_id: int = Field(..., description="Asset ID in database")
    filename: str = Field(..., description="Original filename")
    size: int = Field(..., description="File size in bytes")
    message: str = Field("File uploaded successfully")
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_id": "550e8400-e29b-41d4-a716-446655440000",
                "asset_id": 1,
                "filename": "document.pdf",
                "size": 1024000,
                "message": "File uploaded successfully"
            }
        }


class FileUploadError(BaseModel):
    """Schema for file upload error response"""
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    field: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "FILE_UPLOAD_ERROR",
                "message": "File type not allowed",
                "field": "file"
            }
        }