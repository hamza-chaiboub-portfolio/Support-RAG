"""Schemas package for request/response validation"""

from .project import (
    ProjectCreateRequest,
    ProjectUpdateRequest,
    ProjectResponse,
    ProjectListResponse,
    ProjectStatus,
)
from .asset import (
    AssetCreateRequest,
    AssetResponse,
    FileUploadResponse,
    FileUploadError,
    AssetType,
)

__all__ = [
    # Project schemas
    "ProjectCreateRequest",
    "ProjectUpdateRequest",
    "ProjectResponse",
    "ProjectListResponse",
    "ProjectStatus",
    # Asset schemas
    "AssetCreateRequest",
    "AssetResponse",
    "FileUploadResponse",
    "FileUploadError",
    "AssetType",
]