"""CSRF protection middleware using double-submit cookie pattern"""

import secrets
import os
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from helpers.logger import logger

try:
    from helpers.config import get_settings
except ImportError:
    from src.helpers.config import get_settings

settings = get_settings()


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    CSRF protection using double-submit cookie pattern.
    - Safe methods (GET, HEAD, OPTIONS) don't need CSRF tokens
    - Unsafe methods require matching token in header and cookie
    """
    
    CSRF_COOKIE_NAME = "csrf_token"
    CSRF_HEADER_NAME = "x-csrf-token"
    SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}
    TOKEN_LENGTH = 32
    
    async def dispatch(self, request: Request, call_next):
        # Skip CSRF validation in testing mode
        if os.getenv("TESTING") == "true":
            return await call_next(request)
        
        # Generate CSRF token if not present
        csrf_cookie = request.cookies.get(self.CSRF_COOKIE_NAME)
        
        if not csrf_cookie:
            csrf_token = secrets.token_hex(self.TOKEN_LENGTH)
        else:
            csrf_token = csrf_cookie
        
        # For unsafe methods, validate CSRF token
        if request.method not in self.SAFE_METHODS:
            csrf_header = request.headers.get(self.CSRF_HEADER_NAME, "")
            
            if not csrf_cookie:
                logger.warning(
                    f"CSRF: Missing cookie for {request.method} {request.url.path}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="CSRF token missing"
                )
            
            if csrf_header != csrf_cookie:
                logger.warning(
                    f"CSRF: Token mismatch for {request.method} {request.url.path}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="CSRF token invalid"
                )
        
        # Attach token to request state so endpoints can use it
        request.state.csrf_token = csrf_token
        
        try:
            response = await call_next(request)
        except HTTPException as e:
            # Re-raise HTTPExceptions so they can be handled by FastAPI's exception handlers
            raise e
        except Exception as e:
            logger.error(f"Error in CSRF middleware dispatch: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise e
        
        # Set CSRF token in cookie
        response.set_cookie(
            key=self.CSRF_COOKIE_NAME,
            value=csrf_token,
            max_age=3600 * 24,  # 24 hours
            httponly=False,  # Must be readable by JS for header
            secure=settings.ENV == "production",  # Only True in production
            samesite="Lax" if settings.ENV != "production" else "Strict"
        )
        
        return response
