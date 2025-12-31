from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from helpers.database import get_db
from helpers.config import get_settings
from controllers.ApiKeyController import ApiKeyController

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
security = HTTPBearer(auto_error=False)

async def get_current_user_or_api_key(
    api_key: str = Security(api_key_header),
    bearer: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Authenticate using either API Key or JWT Bearer token.
    Returns a dict with user info (similar to JWT payload).
    """
    
    # 1. Try API Key
    if api_key:
        key_obj = await ApiKeyController.verify_api_key(db, api_key)
        if key_obj:
            return {
                "user_id": key_obj.user_id,
                "sub": f"apikey:{key_obj.id}",
                "auth_type": "api_key",
                # We could fetch role here if needed, but for now assume basic access
                # If role is critical, we should fetch the user.
                "role": "user" 
            }
        else:
            # Invalid API Key provided
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API Key"
            )

    # 2. Try Bearer Token (JWT)
    if bearer:
        try:
            settings = get_settings()
            token = bearer.credentials
            
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            payload["auth_type"] = "jwt"
            return payload
            
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

    # 3. No auth provided
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated"
    )
