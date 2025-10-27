from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from helpers.config import get_settings, Settings
from helpers.jwt_handler import create_access_token

auth_router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth"],
)

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str

@auth_router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    settings: Settings = Depends(get_settings)
):
    if request.username == "admin" and request.password == "password":
        access_token = create_access_token(
            data={"sub": request.username},
            settings=settings
        )
        return {"access_token": access_token, "token_type": "bearer"}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
    )