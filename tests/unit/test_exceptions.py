"""Unit tests for the exceptions module"""

import pytest
from fastapi import status

from helpers.exceptions import (
    AppException,
    ValidationException,
    ResourceNotFoundException,
    PermissionException,
    DatabaseException,
    FileUploadException,
    ProcessingException,
    AuthenticationException,
    ConfigException,
    app_exception_to_http_exception,
)


@pytest.mark.unit
class TestAppException:
    """Tests for base AppException class"""
    
    def test_app_exception_initialization(self):
        """Test that AppException initializes correctly"""
        exc = AppException("Test error", "TEST_CODE")
        assert exc.message == "Test error"
        assert exc.code == "TEST_CODE"
    
    def test_app_exception_default_code(self):
        """Test that AppException uses default code"""
        exc = AppException("Test error")
        assert exc.code == "APP_ERROR"
    
    def test_app_exception_inheritance(self):
        """Test that AppException inherits from Exception"""
        exc = AppException("Test error")
        assert isinstance(exc, Exception)
    
    def test_app_exception_message_in_string(self):
        """Test that exception message is included in string representation"""
        exc = AppException("Test message")
        assert "Test message" in str(exc)


@pytest.mark.unit
class TestValidationException:
    """Tests for ValidationException class"""
    
    def test_validation_exception_initialization(self):
        """Test that ValidationException initializes correctly"""
        exc = ValidationException("Invalid input")
        assert exc.message == "Invalid input"
        assert exc.code == "VALIDATION_ERROR"
    
    def test_validation_exception_with_field(self):
        """Test that ValidationException stores field information"""
        exc = ValidationException("Invalid email", field="email")
        assert exc.field == "email"
    
    def test_validation_exception_default_field(self):
        """Test that ValidationException field defaults to None"""
        exc = ValidationException("Invalid input")
        assert exc.field is None
    
    def test_validation_exception_inheritance(self):
        """Test that ValidationException inherits from AppException"""
        exc = ValidationException("Invalid input")
        assert isinstance(exc, AppException)


@pytest.mark.unit
class TestResourceNotFoundException:
    """Tests for ResourceNotFoundException class"""
    
    def test_resource_not_found_exception_initialization(self):
        """Test that ResourceNotFoundException initializes correctly"""
        exc = ResourceNotFoundException("Project", 123)
        assert exc.code == "RESOURCE_NOT_FOUND"
        assert exc.resource_type == "Project"
        assert exc.resource_id == 123
    
    def test_resource_not_found_exception_message_format(self):
        """Test that ResourceNotFoundException formats message correctly"""
        exc = ResourceNotFoundException("User", 456)
        assert "User" in exc.message
        assert "456" in exc.message
        assert "not found" in exc.message
    
    def test_resource_not_found_with_string_id(self):
        """Test ResourceNotFoundException with string ID"""
        exc = ResourceNotFoundException("Document", "uuid-123")
        assert "uuid-123" in exc.message
    
    def test_resource_not_found_inheritance(self):
        """Test that ResourceNotFoundException inherits from AppException"""
        exc = ResourceNotFoundException("Project", 1)
        assert isinstance(exc, AppException)


@pytest.mark.unit
class TestPermissionException:
    """Tests for PermissionException class"""
    
    def test_permission_exception_initialization(self):
        """Test that PermissionException initializes correctly"""
        exc = PermissionException()
        assert exc.message == "Permission denied"
        assert exc.code == "PERMISSION_DENIED"
    
    def test_permission_exception_custom_message(self):
        """Test that PermissionException accepts custom message"""
        exc = PermissionException("Cannot delete admin users")
        assert exc.message == "Cannot delete admin users"
    
    def test_permission_exception_inheritance(self):
        """Test that PermissionException inherits from AppException"""
        exc = PermissionException()
        assert isinstance(exc, AppException)


@pytest.mark.unit
class TestDatabaseException:
    """Tests for DatabaseException class"""
    
    def test_database_exception_initialization(self):
        """Test that DatabaseException initializes correctly"""
        exc = DatabaseException("Connection failed")
        assert exc.message == "Connection failed"
        assert exc.code == "DATABASE_ERROR"
    
    def test_database_exception_with_operation(self):
        """Test that DatabaseException stores operation information"""
        exc = DatabaseException("Insert failed", operation="INSERT")
        assert exc.operation == "INSERT"
    
    def test_database_exception_default_operation(self):
        """Test that DatabaseException operation defaults to None"""
        exc = DatabaseException("Connection failed")
        assert exc.operation is None
    
    def test_database_exception_inheritance(self):
        """Test that DatabaseException inherits from AppException"""
        exc = DatabaseException("Connection failed")
        assert isinstance(exc, AppException)


@pytest.mark.unit
class TestFileUploadException:
    """Tests for FileUploadException class"""
    
    def test_file_upload_exception_initialization(self):
        """Test that FileUploadException initializes correctly"""
        exc = FileUploadException("Upload failed")
        assert exc.message == "Upload failed"
        assert exc.code == "FILE_UPLOAD_ERROR"
    
    def test_file_upload_exception_with_reason(self):
        """Test that FileUploadException stores reason information"""
        exc = FileUploadException("Upload failed", reason="File too large")
        assert exc.reason == "File too large"
    
    def test_file_upload_exception_default_reason(self):
        """Test that FileUploadException reason defaults to None"""
        exc = FileUploadException("Upload failed")
        assert exc.reason is None
    
    def test_file_upload_exception_inheritance(self):
        """Test that FileUploadException inherits from AppException"""
        exc = FileUploadException("Upload failed")
        assert isinstance(exc, AppException)


@pytest.mark.unit
class TestProcessingException:
    """Tests for ProcessingException class"""
    
    def test_processing_exception_initialization(self):
        """Test that ProcessingException initializes correctly"""
        exc = ProcessingException("Processing failed")
        assert exc.message == "Processing failed"
        assert exc.code == "PROCESSING_ERROR"
    
    def test_processing_exception_with_step(self):
        """Test that ProcessingException stores step information"""
        exc = ProcessingException("Processing failed", step="tokenization")
        assert exc.step == "tokenization"
    
    def test_processing_exception_default_step(self):
        """Test that ProcessingException step defaults to None"""
        exc = ProcessingException("Processing failed")
        assert exc.step is None
    
    def test_processing_exception_inheritance(self):
        """Test that ProcessingException inherits from AppException"""
        exc = ProcessingException("Processing failed")
        assert isinstance(exc, AppException)


@pytest.mark.unit
class TestAuthenticationException:
    """Tests for AuthenticationException class"""
    
    def test_authentication_exception_initialization(self):
        """Test that AuthenticationException initializes correctly"""
        exc = AuthenticationException()
        assert exc.message == "Authentication failed"
        assert exc.code == "AUTHENTICATION_ERROR"
    
    def test_authentication_exception_custom_message(self):
        """Test that AuthenticationException accepts custom message"""
        exc = AuthenticationException("Invalid credentials")
        assert exc.message == "Invalid credentials"
    
    def test_authentication_exception_inheritance(self):
        """Test that AuthenticationException inherits from AppException"""
        exc = AuthenticationException()
        assert isinstance(exc, AppException)


@pytest.mark.unit
class TestConfigException:
    """Tests for ConfigException class"""
    
    def test_config_exception_initialization(self):
        """Test that ConfigException initializes correctly"""
        exc = ConfigException("Invalid configuration")
        assert exc.message == "Invalid configuration"
        assert exc.code == "CONFIG_ERROR"
    
    def test_config_exception_with_config_key(self):
        """Test that ConfigException stores config key information"""
        exc = ConfigException("Missing required key", config_key="JWT_SECRET_KEY")
        assert exc.config_key == "JWT_SECRET_KEY"
    
    def test_config_exception_default_config_key(self):
        """Test that ConfigException config_key defaults to None"""
        exc = ConfigException("Invalid configuration")
        assert exc.config_key is None
    
    def test_config_exception_inheritance(self):
        """Test that ConfigException inherits from AppException"""
        exc = ConfigException("Invalid configuration")
        assert isinstance(exc, AppException)


@pytest.mark.unit
class TestAppExceptionToHttpException:
    """Tests for app_exception_to_http_exception converter function"""
    
    def test_convert_validation_exception(self):
        """Test converting ValidationException to HTTPException"""
        exc = ValidationException("Invalid input", field="email")
        http_exc = app_exception_to_http_exception(exc)
        
        assert http_exc.status_code == status.HTTP_400_BAD_REQUEST
        assert http_exc.detail["error"] == "VALIDATION_ERROR"
        assert http_exc.detail["message"] == "Invalid input"
        assert http_exc.detail["field"] == "email"
    
    def test_convert_authentication_exception(self):
        """Test converting AuthenticationException to HTTPException"""
        exc = AuthenticationException("Invalid token")
        http_exc = app_exception_to_http_exception(exc)
        
        assert http_exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert http_exc.detail["error"] == "AUTHENTICATION_ERROR"
        assert http_exc.detail["message"] == "Invalid token"
    
    def test_convert_permission_exception(self):
        """Test converting PermissionException to HTTPException"""
        exc = PermissionException("Insufficient permissions")
        http_exc = app_exception_to_http_exception(exc)
        
        assert http_exc.status_code == status.HTTP_403_FORBIDDEN
        assert http_exc.detail["error"] == "PERMISSION_DENIED"
    
    def test_convert_resource_not_found_exception(self):
        """Test converting ResourceNotFoundException to HTTPException"""
        exc = ResourceNotFoundException("Project", 123)
        http_exc = app_exception_to_http_exception(exc)
        
        assert http_exc.status_code == status.HTTP_404_NOT_FOUND
        assert http_exc.detail["error"] == "RESOURCE_NOT_FOUND"
        assert http_exc.detail["resource_type"] == "Project"
    
    def test_convert_file_upload_exception(self):
        """Test converting FileUploadException to HTTPException"""
        exc = FileUploadException("Upload failed", reason="File too large")
        http_exc = app_exception_to_http_exception(exc)
        
        assert http_exc.status_code == status.HTTP_400_BAD_REQUEST
        assert http_exc.detail["error"] == "FILE_UPLOAD_ERROR"
        assert http_exc.detail["reason"] == "File too large"
    
    def test_convert_processing_exception(self):
        """Test converting ProcessingException to HTTPException"""
        exc = ProcessingException("Processing failed", step="tokenization")
        http_exc = app_exception_to_http_exception(exc)
        
        assert http_exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert http_exc.detail["error"] == "PROCESSING_ERROR"
    
    def test_convert_database_exception(self):
        """Test converting DatabaseException to HTTPException"""
        exc = DatabaseException("Connection failed", operation="SELECT")
        http_exc = app_exception_to_http_exception(exc)
        
        assert http_exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert http_exc.detail["error"] == "DATABASE_ERROR"
    
    def test_convert_config_exception(self):
        """Test converting ConfigException to HTTPException"""
        exc = ConfigException("Invalid configuration", config_key="JWT_SECRET_KEY")
        http_exc = app_exception_to_http_exception(exc)
        
        assert http_exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert http_exc.detail["error"] == "CONFIG_ERROR"
    
    def test_convert_generic_app_exception(self):
        """Test converting generic AppException to HTTPException"""
        exc = AppException("Something went wrong")
        http_exc = app_exception_to_http_exception(exc)
        
        assert http_exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert http_exc.detail["error"] == "APP_ERROR"
    
    def test_http_exception_detail_format(self):
        """Test that HTTP exception detail always has error and message"""
        exc = ValidationException("Test error")
        http_exc = app_exception_to_http_exception(exc)
        
        assert "error" in http_exc.detail
        assert "message" in http_exc.detail
    
    def test_http_exception_no_optional_fields_when_none(self):
        """Test that optional fields are not included when they are None"""
        exc = ValidationException("Test error")
        http_exc = app_exception_to_http_exception(exc)
        
        assert "field" not in http_exc.detail
    
    def test_unknown_error_code_defaults_to_500(self):
        """Test that unknown error codes default to 500 status"""
        exc = AppException("Unknown error", "UNKNOWN_CODE")
        http_exc = app_exception_to_http_exception(exc)
        
        assert http_exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.unit
class TestExceptionEdgeCases:
    """Tests for edge cases and special scenarios"""
    
    def test_exception_with_special_characters(self):
        """Test exception with special characters in message"""
        exc = ValidationException("Invalid: <>&\"'")
        assert exc.message == "Invalid: <>&\"'"
    
    def test_exception_with_unicode_characters(self):
        """Test exception with unicode characters"""
        exc = ValidationException("Erreur: données invalides ñ日本語")
        assert "Erreur" in exc.message
    
    def test_exception_with_very_long_message(self):
        """Test exception with very long message"""
        long_message = "A" * 1000
        exc = ValidationException(long_message)
        assert exc.message == long_message
    
    def test_exception_with_zero_id(self):
        """Test ResourceNotFoundException with zero ID"""
        exc = ResourceNotFoundException("Resource", 0)
        assert "0" in exc.message
    
    def test_exception_with_negative_id(self):
        """Test ResourceNotFoundException with negative ID"""
        exc = ResourceNotFoundException("Resource", -1)
        assert "-1" in exc.message
    
    def test_http_exception_preserves_all_attributes(self):
        """Test that conversion to HTTP exception preserves all attributes"""
        exc = ProcessingException("Failed at step", step="parsing")
        http_exc = app_exception_to_http_exception(exc)
        
        assert http_exc.detail["message"] == "Failed at step"
        assert http_exc.detail["error"] == "PROCESSING_ERROR"
