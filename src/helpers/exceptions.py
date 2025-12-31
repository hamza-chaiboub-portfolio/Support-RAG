"""Custom exception classes for the application"""

from fastapi import HTTPException, status
from typing import Optional, Any, Dict


class AppException(Exception):
    """Base exception for the application"""
    
    def __init__(self, message: str, code: str = "APP_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ValidationException(AppException):
    """Raised when input validation fails"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field


class ResourceNotFoundException(AppException):
    """Raised when a requested resource is not found"""
    
    def __init__(self, resource_type: str, resource_id: Any):
        message = f"{resource_type} with id {resource_id} not found"
        super().__init__(message, "RESOURCE_NOT_FOUND")
        self.resource_type = resource_type
        self.resource_id = resource_id


class PermissionException(AppException):
    """Raised when user doesn't have required permissions"""
    
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, "PERMISSION_DENIED")


class DatabaseException(AppException):
    """Raised when database operation fails"""
    
    def __init__(self, message: str, operation: Optional[str] = None):
        super().__init__(message, "DATABASE_ERROR")
        self.operation = operation


class FileUploadException(AppException):
    """Raised when file upload fails"""
    
    def __init__(self, message: str, reason: Optional[str] = None):
        super().__init__(message, "FILE_UPLOAD_ERROR")
        self.reason = reason


class ProcessingException(AppException):
    """Raised when data processing fails"""
    
    def __init__(self, message: str, step: Optional[str] = None):
        super().__init__(message, "PROCESSING_ERROR")
        self.step = step


class AuthenticationException(AppException):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTHENTICATION_ERROR")


class ConfigException(AppException):
    """Raised when configuration is invalid"""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(message, "CONFIG_ERROR")
        self.config_key = config_key


def app_exception_to_http_exception(exc: AppException) -> HTTPException:
    """
    Convert application exception to FastAPI HTTPException
    
    Args:
        exc: Application exception
        
    Returns:
        HTTPException suitable for FastAPI response
    """
    
    status_code_map = {
        "VALIDATION_ERROR": status.HTTP_400_BAD_REQUEST,
        "AUTHENTICATION_ERROR": status.HTTP_401_UNAUTHORIZED,
        "PERMISSION_DENIED": status.HTTP_403_FORBIDDEN,
        "RESOURCE_NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "FILE_UPLOAD_ERROR": status.HTTP_400_BAD_REQUEST,
        "PROCESSING_ERROR": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "DATABASE_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "CONFIG_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "APP_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
    }
    
    http_status = status_code_map.get(exc.code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    detail: Dict[str, Any] = {
        "error": exc.code,
        "message": exc.message,
    }
    
    # Add additional context if available
    if hasattr(exc, 'field') and exc.field:
        detail["field"] = exc.field
    if hasattr(exc, 'resource_type') and exc.resource_type:
        detail["resource_type"] = exc.resource_type
    if hasattr(exc, 'reason') and exc.reason:
        detail["reason"] = exc.reason
    
    return HTTPException(status_code=http_status, detail=detail)