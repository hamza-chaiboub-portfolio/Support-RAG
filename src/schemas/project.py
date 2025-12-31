"""Pydantic schemas for Project-related requests and responses"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
from helpers.sanitization import sanitize_input


class ProjectStatus(str, Enum):
    """Project status options"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class ProjectCreateRequest(BaseModel):
    """Schema for creating a new project"""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=2000, description="Project description")
    
    @field_validator('name', 'description')
    @classmethod
    def sanitize_fields(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return sanitize_input(v)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Support Documents",
                "description": "FAQ and support documentation"
            }
        }


class ProjectUpdateRequest(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[ProjectStatus] = None
    
    @field_validator('name', 'description')
    @classmethod
    def sanitize_fields(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return sanitize_input(v)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated Project Name",
                "status": "inactive"
            }
        }


class ProjectResponse(BaseModel):
    """Schema for project response"""
    id: int
    name: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Support Documents",
                "description": "FAQ and support documentation",
                "status": "active",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00"
            }
        }


class ProjectListResponse(BaseModel):
    """Schema for listing projects"""
    total: int = Field(..., description="Total number of projects")
    items: List[ProjectResponse] = Field(..., description="List of projects")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 2,
                "items": [
                    {
                        "id": 1,
                        "name": "Project 1",
                        "description": "Description 1",
                        "status": "active",
                        "created_at": "2024-01-15T10:30:00",
                        "updated_at": "2024-01-15T10:30:00"
                    }
                ]
            }
        }