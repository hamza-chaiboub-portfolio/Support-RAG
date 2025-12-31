from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from helpers.database import get_db
from helpers.jwt_handler import verify_token
from controllers.ApiKeyController import ApiKeyController
from schemas.api_key import ApiKeyCreateRequest, ApiKeyResponse, ApiKeyCreateResponse

api_key_router = APIRouter(
    prefix="/api/v1/api-keys",
    tags=["api-keys"]
)

@api_key_router.post("", response_model=ApiKeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    request: ApiKeyCreateRequest,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token)
):
    """Create a new API Key"""
    user_id = token.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    api_key, raw_key = await ApiKeyController.create_api_key(
        db=db,
        user_id=user_id,
        name=request.name,
        expires_in_days=request.expires_in_days
    )
    
    # Add prefix for display (e.g. sk_...)
    response = ApiKeyCreateResponse.model_validate(api_key)
    response.key = raw_key
    response.prefix = raw_key[:6] + "..."
    
    return response

@api_key_router.get("", response_model=List[ApiKeyResponse])
async def list_api_keys(
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token)
):
    """List my API Keys"""
    user_id = token.get("user_id")
    keys = await ApiKeyController.list_keys(db, user_id)
    
    # Add prefix
    results = []
    for k in keys:
        resp = ApiKeyResponse.model_validate(k)
        resp.prefix = "sk_..." # We don't store the prefix/raw key, but we know the format
        results.append(resp)
        
    return results

@api_key_router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: int,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token)
):
    """Revoke an API Key"""
    user_id = token.get("user_id")
    success = await ApiKeyController.revoke_key(db, key_id, user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="API Key not found")
