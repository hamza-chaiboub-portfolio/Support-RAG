"""Data/Asset business logic controller"""

import logging
import os
import uuid
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet

from sqlalchemy.ext.asyncio import AsyncSession

from helpers.config import get_settings
from helpers.exceptions import (
    ResourceNotFoundException,
    ValidationException,
    DatabaseException,
    FileUploadException,
)
from helpers.logger import setup_logger
from helpers.sanitization import sanitize_filename
from models.db_models import Asset, AssetType
from repositories import ProjectRepository, AssetRepository
from schemas import FileUploadResponse

logger = setup_logger(__name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.docx', '.doc', '.md', '.json'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


class DataController:
    """Controller for data/asset-related business logic"""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize data controller
        
        Args:
            db: Database session
        """
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.asset_repo = AssetRepository(db)
        self.logger = logger
        self.data_dir = Path("./data/projects")
        
        # Initialize encryption
        settings = get_settings()
        try:
            self.fernet = Fernet(settings.ENCRYPTION_KEY.encode())
        except Exception:
            # Fallback for development if key is invalid/missing
            # In production this should raise an error
            self.logger.warning("Invalid ENCRYPTION_KEY, using temporary key. DATA WILL BE UNREADABLE AFTER RESTART.")
            self.fernet = Fernet(Fernet.generate_key())

    def _encrypt_content(self, content: bytes) -> bytes:
        """Encrypt content before saving"""
        return self.fernet.encrypt(content)

    def _decrypt_content(self, content: bytes) -> bytes:
        """Decrypt content after reading"""
        return self.fernet.decrypt(content)
    
    def _validate_file_magic_number(self, content: bytes, ext: str) -> bool:
        """
        Validate file content against magic numbers
        """
        if not content:
            return False
            
        # Magic numbers for common file types
        signatures = {
            '.pdf': [b'%PDF-'],
            '.png': [b'\x89PNG\r\n\x1a\n'],
            '.jpg': [b'\xff\xd8\xff'],
            '.jpeg': [b'\xff\xd8\xff'],
            '.zip': [b'PK\x03\x04'],
            '.docx': [b'PK\x03\x04'],  # DOCX is a zip
        }
        
        # Text files don't have reliable magic numbers, so we skip them
        if ext in ['.txt', '.md', '.json', '.csv']:
            return True
            
        sigs = signatures.get(ext)
        if not sigs:
            return True  # Unknown type, rely on extension (or block if strict)
            
        for sig in sigs:
            if content.startswith(sig):
                return True
                
        return False

    async def upload_file(
        self,
        project_id: int,
        filename: str,
        file_contents: bytes
    ) -> FileUploadResponse:
        """
        Upload a file to a project
        
        Args:
            project_id: Project ID
            filename: Original filename
            file_contents: File content bytes
            
        Returns:
            File upload response
            
        Raises:
            ResourceNotFoundException: If project not found
            ValidationException: If validation fails
            FileUploadException: If upload fails
            DatabaseException: If database operation fails
        """
        try:
            # Validate project exists
            project = await self.project_repo.get_project(project_id)
            if not project:
                raise ResourceNotFoundException("Project", project_id)
            
            # Sanitize filename
            filename = sanitize_filename(filename)
            
            # Validate filename
            if not filename or len(filename.strip()) == 0:
                raise ValidationException("Filename cannot be empty", field="filename")
            
            # Validate file extension
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                raise FileUploadException(
                    f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
                    reason="invalid_extension"
                )
            
            # Validate file size
            if len(file_contents) > MAX_FILE_SIZE:
                raise FileUploadException(
                    f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / 1024 / 1024}MB",
                    reason="file_too_large"
                )
            
            if len(file_contents) == 0:
                raise FileUploadException("File is empty", reason="empty_file")
                
            # Validate magic number
            if not self._validate_file_magic_number(file_contents, file_ext):
                raise FileUploadException(
                    "File content does not match extension",
                    reason="invalid_content"
                )
            
            self.logger.info(f"Uploading file: {filename} to project {project_id}")
            
            # Generate unique file ID
            file_id = str(uuid.uuid4())
            
            # Create project directory
            project_dir = self.data_dir / str(project_id)
            project_dir.mkdir(parents=True, exist_ok=True)
            
            # Construct safe file path
            file_path = project_dir / f"{file_id}{file_ext}"
            
            # Save file
            try:
                encrypted_content = self._encrypt_content(file_contents)
                with open(file_path, 'wb') as f:
                    f.write(encrypted_content)
            except IOError as e:
                raise FileUploadException(f"Failed to save file: {str(e)}", reason="disk_error")
            
            # Determine asset type from file extension
            asset_type_map = {
                '.pdf': AssetType.PDF,
                '.txt': AssetType.TEXT,
                '.md': AssetType.MARKDOWN,
                '.docx': AssetType.DOCUMENT,
                '.doc': AssetType.DOCUMENT,
                '.json': AssetType.TEXT
            }
            asset_type = asset_type_map.get(file_ext, AssetType.DOCUMENT)
            
            # Save asset to database
            asset = await self.asset_repo.create_asset(
                project_id=project_id,
                filename=filename,
                asset_type=asset_type.value,
                file_path=str(file_path),
                file_size=len(file_contents)
            )
            
            self.logger.info(f"File uploaded successfully: {file_id} (asset_id={asset.id})")
            
            return FileUploadResponse(
                file_id=file_id,
                asset_id=asset.id,
                filename=filename,
                size=len(file_contents)
            )
            
        except (ResourceNotFoundException, ValidationException, FileUploadException):
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during file upload: {str(e)}")
            raise DatabaseException(f"File upload failed: {str(e)}", operation="upload")
    
    async def delete_asset(self, project_id: int, asset_id: int) -> bool:
        """
        Delete an asset and its file
        
        Args:
            project_id: Project ID
            asset_id: Asset ID
            
        Returns:
            True if deleted successfully
            
        Raises:
            ResourceNotFoundException: If project or asset not found
            FileUploadException: If file deletion fails
            DatabaseException: If database operation fails
        """
        try:
            # Validate project exists
            project = await self.project_repo.get_project(project_id)
            if not project:
                raise ResourceNotFoundException("Project", project_id)
            
            # Get asset
            asset = await self.asset_repo.get_asset(asset_id)
            if not asset or asset.project_id != project_id:
                raise ResourceNotFoundException("Asset", asset_id)
            
            self.logger.info(f"Deleting asset {asset_id} from project {project_id}")
            
            # Delete file from disk
            try:
                file_path = Path(asset.file_path)
                if file_path.exists():
                    file_path.unlink()
            except OSError as e:
                self.logger.warning(f"Failed to delete file from disk: {str(e)}")
                # Continue with database deletion even if file deletion fails
            
            # Delete asset from database
            await self.asset_repo.delete_asset(asset_id)
            
            self.logger.info(f"Asset {asset_id} deleted successfully")
            return True
            
        except (ResourceNotFoundException, FileUploadException):
            raise
        except Exception as e:
            self.logger.error(f"Failed to delete asset {asset_id}: {str(e)}")
            raise DatabaseException(f"Failed to delete asset: {str(e)}", operation="delete")
    
    async def get_asset_content(self, asset_id: int) -> bytes:
        """
        Get decrypted asset content
        """
        try:
            asset = await self.asset_repo.get_asset(asset_id)
            if not asset:
                raise ResourceNotFoundException("Asset", asset_id)
                
            file_path = Path(asset.file_path)
            if not file_path.exists():
                raise ResourceNotFoundException("File", str(file_path))
                
            with open(file_path, 'rb') as f:
                encrypted_content = f.read()
                
            return self._decrypt_content(encrypted_content)
            
        except Exception as e:
            self.logger.error(f"Failed to read asset content: {str(e)}")
            raise DatabaseException(f"Failed to read asset: {str(e)}", operation="read")

    async def get_asset_details(self, asset_id: int) -> dict:
        """
        Get detailed information about an asset
        
        Args:
            asset_id: Asset ID
            
        Returns:
            Asset details dictionary
            
        Raises:
            ResourceNotFoundException: If asset not found
            DatabaseException: If database operation fails
        """
        try:
            asset = await self.asset_repo.get_asset(asset_id)
            if not asset:
                raise ResourceNotFoundException("Asset", asset_id)
            
            # Check if file exists
            file_path = Path(asset.file_path)
            file_exists = file_path.exists()
            
            return {
                "id": asset.id,
                "project_id": asset.project_id,
                "filename": asset.filename,
                "asset_type": asset.asset_type,
                "file_size": asset.file_size,
                "file_path": asset.file_path,
                "file_exists": file_exists,
                "created_at": asset.created_at,
            }
            
        except ResourceNotFoundException:
            raise
        except Exception as e:
            self.logger.error(f"Failed to get asset details: {str(e)}")
            raise DatabaseException(f"Failed to retrieve asset details: {str(e)}", operation="read")