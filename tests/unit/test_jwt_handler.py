"""Unit tests for the JWT handler module"""

import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from helpers.jwt_handler import (
    create_access_token,
    verify_token,
    get_current_user,
    security,
)
from helpers.config import Settings


@pytest.mark.unit
class TestCreateAccessToken:
    """Tests for token creation"""
    
    def test_create_access_token_basic(self):
        """Test basic token creation"""
        settings = Settings()
        data = {"sub": "user123"}
        
        token = create_access_token(data, settings)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_contains_payload(self):
        """Test that created token contains the payload data"""
        settings = Settings()
        data = {"sub": "user123"}
        
        token = create_access_token(data, settings)
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        assert decoded["sub"] == "user123"
    
    def test_create_access_token_contains_expiration(self):
        """Test that created token contains expiration"""
        settings = Settings()
        data = {"sub": "user123"}
        
        token = create_access_token(data, settings)
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        assert "exp" in decoded
        assert isinstance(decoded["exp"], (int, float))
    
    def test_create_access_token_expiration_is_in_future(self):
        """Test that expiration time is in the future"""
        settings = Settings()
        data = {"sub": "user123"}
        now = datetime.utcnow()
        
        token = create_access_token(data, settings)
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        exp_time = datetime.fromtimestamp(decoded["exp"])
        assert exp_time > now
    
    def test_create_access_token_with_multiple_claims(self):
        """Test token creation with multiple claims"""
        settings = Settings()
        data = {"sub": "user123", "role": "admin", "email": "user@example.com"}
        
        token = create_access_token(data, settings)
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        assert decoded["sub"] == "user123"
        assert decoded["role"] == "admin"
        assert decoded["email"] == "user@example.com"
    
    def test_create_access_token_respects_expiration_hours(self):
        """Test that expiration respects JWT_EXPIRATION_HOURS setting"""
        settings = Settings()
        original_hours = settings.JWT_EXPIRATION_HOURS
        data = {"sub": "user123"}
        
        before_now = datetime.utcnow()
        token = create_access_token(data, settings)
        after_now = datetime.utcnow()
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        exp_value = decoded["exp"]
        if isinstance(exp_value, datetime):
            exp_time = exp_value
        else:
            exp_time = datetime.fromtimestamp(exp_value)
        
        expected_duration = timedelta(hours=original_hours).total_seconds()
        actual_duration = (exp_time - before_now).total_seconds()
        
        assert expected_duration - 3600 < actual_duration < expected_duration + 3600
    
    def test_create_access_token_uses_correct_algorithm(self):
        """Test that token uses the correct algorithm"""
        settings = Settings()
        data = {"sub": "user123"}
        
        token = create_access_token(data, settings)
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        assert decoded is not None
    
    def test_create_access_token_does_not_modify_original_data(self):
        """Test that creating token doesn't modify original data"""
        settings = Settings()
        data = {"sub": "user123"}
        original_data = data.copy()
        
        create_access_token(data, settings)
        
        assert data == original_data
    
    def test_create_access_token_with_different_secrets(self):
        """Test that tokens created with different secrets can't decode each other"""
        settings1 = Settings()
        settings1.JWT_SECRET_KEY = "secret1"
        settings2 = Settings()
        settings2.JWT_SECRET_KEY = "secret2"
        data = {"sub": "user123"}
        
        token = create_access_token(data, settings1)
        
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(token, settings2.JWT_SECRET_KEY, algorithms=[settings2.JWT_ALGORITHM])


@pytest.mark.unit
class TestVerifyToken:
    """Tests for token verification"""
    
    def test_verify_token_with_valid_token(self):
        """Test verifying a valid token"""
        settings = Settings()
        data = {"sub": "user123"}
        token = create_access_token(data, settings)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        with patch('helpers.jwt_handler.get_settings', return_value=settings):
            payload = verify_token(credentials, settings)
        
        assert payload["sub"] == "user123"
    
    def test_verify_token_without_credentials(self):
        """Test that missing credentials raises HTTPException"""
        settings = Settings()
        
        with pytest.raises(HTTPException) as exc_info:
            with patch('helpers.jwt_handler.get_settings', return_value=settings):
                verify_token(None, settings)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    
    def test_verify_token_with_expired_token(self):
        """Test that expired token raises HTTPException"""
        settings = Settings()
        settings.JWT_EXPIRATION_HOURS = -1
        data = {"sub": "user123"}
        
        token = create_access_token(data, settings)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        with pytest.raises(HTTPException) as exc_info:
            with patch('helpers.jwt_handler.get_settings', return_value=settings):
                verify_token(credentials, settings)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "expired" in exc_info.value.detail.lower()
    
    def test_verify_token_with_invalid_token(self):
        """Test that invalid token raises HTTPException"""
        settings = Settings()
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid.token.here")
        
        with pytest.raises(HTTPException) as exc_info:
            with patch('helpers.jwt_handler.get_settings', return_value=settings):
                verify_token(credentials, settings)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid" in exc_info.value.detail.lower()
    
    def test_verify_token_with_tampered_token(self):
        """Test that tampered token raises HTTPException"""
        settings = Settings()
        data = {"sub": "user123"}
        token = create_access_token(data, settings)
        
        tampered_token = token[:-5] + "XXXXX"
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=tampered_token)
        
        with pytest.raises(HTTPException) as exc_info:
            with patch('helpers.jwt_handler.get_settings', return_value=settings):
                verify_token(credentials, settings)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_verify_token_preserves_payload(self):
        """Test that verify_token returns complete payload"""
        settings = Settings()
        data = {"sub": "user123", "role": "admin", "email": "user@example.com"}
        token = create_access_token(data, settings)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        with patch('helpers.jwt_handler.get_settings', return_value=settings):
            payload = verify_token(credentials, settings)
        
        assert payload["sub"] == "user123"
        assert payload["role"] == "admin"
        assert payload["email"] == "user@example.com"
    
    def test_verify_token_with_wrong_secret(self):
        """Test that token signed with different secret can't be verified"""
        settings1 = Settings()
        settings1.JWT_SECRET_KEY = "secret1"
        settings2 = Settings()
        settings2.JWT_SECRET_KEY = "secret2"
        
        data = {"sub": "user123"}
        token = create_access_token(data, settings1)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        with pytest.raises(HTTPException) as exc_info:
            with patch('helpers.jwt_handler.get_settings', return_value=settings2):
                verify_token(credentials, settings2)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.unit
class TestGetCurrentUser:
    """Tests for get_current_user function"""
    
    @pytest.mark.asyncio
    async def test_get_current_user_with_valid_payload(self):
        """Test getting current user with valid payload"""
        payload = {"sub": "user123"}
        
        result = await get_current_user(payload)
        
        assert result["user_id"] == "user123"
    
    @pytest.mark.asyncio
    async def test_get_current_user_without_sub_claim(self):
        """Test that missing sub claim raises HTTPException"""
        payload = {"role": "admin"}
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(payload)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_get_current_user_with_none_sub(self):
        """Test that None sub claim raises HTTPException"""
        payload = {"sub": None}
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(payload)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_get_current_user_with_additional_claims(self):
        """Test that additional claims are preserved"""
        payload = {"sub": "user123", "role": "admin"}
        
        result = await get_current_user(payload)
        
        assert result["user_id"] == "user123"
    
    @pytest.mark.asyncio
    async def test_get_current_user_with_different_user_ids(self):
        """Test with different user ID formats"""
        for user_id in ["user1", "123", "uuid-12345", "user@example.com"]:
            payload = {"sub": user_id}
            result = await get_current_user(payload)
            assert result["user_id"] == user_id


@pytest.mark.unit
class TestJWTIntegration:
    """Integration tests for JWT workflow"""
    
    def test_full_jwt_workflow(self):
        """Test complete JWT workflow: create -> verify -> extract user"""
        settings = Settings()
        user_id = "user123"
        
        data = {"sub": user_id}
        token = create_access_token(data, settings)
        
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        with patch('helpers.jwt_handler.get_settings', return_value=settings):
            payload = verify_token(credentials, settings)
        
        assert payload["sub"] == user_id
    
    def test_jwt_workflow_with_admin_user(self):
        """Test JWT workflow with additional admin role"""
        settings = Settings()
        
        data = {"sub": "admin_user", "role": "admin"}
        token = create_access_token(data, settings)
        
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        with patch('helpers.jwt_handler.get_settings', return_value=settings):
            payload = verify_token(credentials, settings)
        
        assert payload["sub"] == "admin_user"
        assert payload["role"] == "admin"


@pytest.mark.unit
class TestJWTEdgeCases:
    """Tests for edge cases"""
    
    def test_create_token_with_empty_data(self):
        """Test creating token with empty data dict"""
        settings = Settings()
        data = {}
        
        token = create_access_token(data, settings)
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        assert "exp" in decoded
    
    def test_create_token_with_unicode_payload(self):
        """Test creating token with unicode characters"""
        settings = Settings()
        data = {"sub": "user_日本語_ñ"}
        
        token = create_access_token(data, settings)
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        assert "日本語" in decoded["sub"]
    
    def test_create_token_with_special_characters(self):
        """Test creating token with special characters"""
        settings = Settings()
        data = {"sub": "user@example.com", "email": "test+test@example.com"}
        
        token = create_access_token(data, settings)
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        assert "@" in decoded["sub"]
        assert "+" in decoded["email"]
    
    def test_token_algorithm_consistency(self):
        """Test that algorithm is consistent"""
        settings = Settings()
        assert settings.JWT_ALGORITHM == "HS256"
        
        data = {"sub": "user123"}
        token = create_access_token(data, settings)
        
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert decoded is not None
    
    def test_verify_token_with_empty_scheme(self):
        """Test verify with empty scheme"""
        settings = Settings()
        data = {"sub": "user123"}
        token = create_access_token(data, settings)
        credentials = HTTPAuthorizationCredentials(scheme="", credentials=token)
        
        with patch('helpers.jwt_handler.get_settings', return_value=settings):
            payload = verify_token(credentials, settings)
        
        assert payload["sub"] == "user123"
    
    def test_expiration_boundary(self):
        """Test token expiration at boundary"""
        settings = Settings()
        hours = settings.JWT_EXPIRATION_HOURS
        data = {"sub": "user123"}
        
        token = create_access_token(data, settings)
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        exp_time = datetime.fromtimestamp(decoded["exp"])
        now = datetime.utcnow()
        duration = (exp_time - now).total_seconds()
        
        expected_seconds = hours * 3600
        assert expected_seconds - 3600 < duration < expected_seconds + 3600
