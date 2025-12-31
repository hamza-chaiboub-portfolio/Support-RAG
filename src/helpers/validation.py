from typing import Any, Optional, Dict
import re
import html
from datetime import datetime
from helpers.exceptions import ValidationException


class InputValidator:
    """Comprehensive input validation utilities"""
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email format and sanitize"""
        if not email or not isinstance(email, str):
            raise ValidationException("Email is required", field="email")
        
        email = email.strip().lower()
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email):
            raise ValidationException("Invalid email format", field="email")
        
        if len(email) > 254:
            raise ValidationException("Email too long", field="email")
        
        return email
    
    @staticmethod
    def validate_password(password: str) -> str:
        """Validate password strength"""
        if not password or not isinstance(password, str):
            raise ValidationException("Password is required", field="password")
        
        if len(password) < 8:
            raise ValidationException("Password must be at least 8 characters", field="password")
        
        if len(password) > 128:
            raise ValidationException("Password too long", field="password")
        
        if not re.search(r'[A-Z]', password):
            raise ValidationException("Password must contain uppercase letter", field="password")
        
        if not re.search(r'[a-z]', password):
            raise ValidationException("Password must contain lowercase letter", field="password")
        
        if not re.search(r'\d', password):
            raise ValidationException("Password must contain number", field="password")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationException("Password must contain special character", field="password")
        
        return password
    
    @staticmethod
    def validate_username(username: str) -> str:
        """Validate username format"""
        if not username or not isinstance(username, str):
            raise ValidationException("Username is required", field="username")
        
        username = username.strip()
        
        if len(username) < 3:
            raise ValidationException("Username must be at least 3 characters", field="username")
        
        if len(username) > 30:
            raise ValidationException("Username too long", field="username")
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            raise ValidationException("Username can only contain letters, numbers, hyphens, and underscores", field="username")
        
        return username
    
    @staticmethod
    def sanitize_html_content(content: str) -> str:
        """Advanced HTML sanitization"""
        if not content or not isinstance(content, str):
            return content
        
        content = re.sub(r'<[^>]*>', '', content)
        content = html.escape(content)
        
        dangerous_patterns = [
            r'javascript:', r'vbscript:', r'onload', r'onerror',
            r'onclick', r'onmouseover', r'onsubmit', r'onfocus',
            r'<script', r'</script>', r'<iframe', r'</iframe>',
            r'eval\s*\(', r'expression\s*\(', r'data:text/html'
        ]
        
        for pattern in dangerous_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        return content.strip()
    
    @staticmethod
    def validate_consent_data(data: dict) -> dict:
        """Validate GDPR consent data"""
        if not isinstance(data, dict):
            raise ValidationException("Consent data must be a dictionary", field="consent_data")
        
        required_fields = ['consent_given', 'consent_date', 'purpose']
        
        for field in required_fields:
            if field not in data:
                raise ValidationException(f"Missing required consent field: {field}", field=field)
        
        if not isinstance(data['consent_given'], bool):
            raise ValidationException("consent_given must be boolean", field="consent_given")
        
        try:
            datetime.fromisoformat(data['consent_date'])
        except (ValueError, TypeError):
            raise ValidationException("consent_date must be valid ISO format", field="consent_date")
        
        if not isinstance(data['purpose'], str) or len(data['purpose'].strip()) == 0:
            raise ValidationException("purpose must be non-empty string", field="purpose")
        
        return data

    @staticmethod
    def validate_string_field(value: str, field_name: str, min_length: int = 1, max_length: int = 1000) -> str:
        """Validate a generic string field"""
        if not isinstance(value, str):
            raise ValidationException(f"{field_name} must be a string", field=field_name)
        
        value = value.strip()
        
        if len(value) < min_length:
            raise ValidationException(f"{field_name} must be at least {min_length} characters", field=field_name)
        
        if len(value) > max_length:
            raise ValidationException(f"{field_name} must not exceed {max_length} characters", field=field_name)
        
        return value

    @staticmethod
    def validate_url(url: str) -> str:
        """Validate URL format"""
        if not url or not isinstance(url, str):
            raise ValidationException("URL is required", field="url")
        
        url = url.strip()
        pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
        
        if not re.match(pattern, url):
            raise ValidationException("Invalid URL format", field="url")
        
        if len(url) > 2048:
            raise ValidationException("URL too long", field="url")
        
        return url

    @staticmethod
    def validate_phone_number(phone: str) -> str:
        """Validate phone number format"""
        if not phone or not isinstance(phone, str):
            raise ValidationException("Phone number is required", field="phone")
        
        phone = re.sub(r'[^\d+\-\s()]', '', phone.strip())
        
        if len(phone) < 7 or len(phone) > 20:
            raise ValidationException("Invalid phone number length", field="phone")
        
        return phone

    @staticmethod
    def validate_integer_range(value: int, field_name: str, min_val: Optional[int] = None, max_val: Optional[int] = None) -> int:
        """Validate integer is within range"""
        if not isinstance(value, int):
            raise ValidationException(f"{field_name} must be an integer", field=field_name)
        
        if min_val is not None and value < min_val:
            raise ValidationException(f"{field_name} must be at least {min_val}", field=field_name)
        
        if max_val is not None and value > max_val:
            raise ValidationException(f"{field_name} must not exceed {max_val}", field=field_name)
        
        return value

    @staticmethod
    def sanitize_dict(data: dict, allowed_keys: Optional[list] = None) -> dict:
        """Sanitize dictionary by filtering keys and HTML content in string values"""
        if not isinstance(data, dict):
            raise ValidationException("Input must be a dictionary", field="data")
        
        sanitized = {}
        
        for key, value in data.items():
            if allowed_keys and key not in allowed_keys:
                continue
            
            if isinstance(value, str):
                sanitized[key] = InputValidator.sanitize_html_content(value)
            elif isinstance(value, dict):
                sanitized[key] = InputValidator.sanitize_dict(value, allowed_keys=None)
            elif isinstance(value, list):
                sanitized[key] = [
                    InputValidator.sanitize_html_content(item) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized
