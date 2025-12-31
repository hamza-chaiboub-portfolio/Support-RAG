from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ApiKeyCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Friendly name for the API Key")
    expires_in_days: Optional[int] = Field(None, ge=1, le=365, description="Expiration in days")

class ApiKeyResponse(BaseModel):
    id: int
    name: str
    prefix: str
    created_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True

class ApiKeyCreateResponse(ApiKeyResponse):
    key: str = Field(..., description="The raw API key. Save this now, it won't be shown again.")
