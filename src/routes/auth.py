import sys
import secrets
from pathlib import Path
from fastapi import APIRouter, HTTPException, status, Depends, Request, Response
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.insert(0, str(Path(__file__).parent.parent))

from helpers.config import get_settings, Settings
from helpers.jwt_handler import create_access_token
from helpers.database import get_db
from helpers.limiter import limiter
from helpers.logger import logger
from helpers.validation import InputValidator
from helpers.exceptions import app_exception_to_http_exception, ValidationException
from controllers.UserController import UserController
from models.user import UserRole

auth_router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth"],
)

@auth_router.get("/csrf")
async def get_csrf_token(request: Request):
    """
    Get CSRF token for unsafe methods.
    The middleware sets the cookie, we just return the token value.
    """
    # The middleware should have attached the token to request.state
    # If not (e.g. middleware disabled), generate one but it won't match cookie unless middleware runs
    csrf_token = getattr(request.state, "csrf_token", None)
    
    if not csrf_token:
        # Fallback if middleware didn't run or didn't set it
        # This shouldn't happen if middleware is active
        csrf_token = secrets.token_hex(32)
    
    return {"csrf_token": csrf_token}

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=8, max_length=255)

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=255)

class RegisterResponse(BaseModel):
    user_id: int
    username: str
    email: str
    message: str

class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)

@auth_router.post("/register", response_model=RegisterResponse, status_code=201)
@limiter.limit("5/hour")
async def register(
    request: Request,
    user_data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
):
    """Register a new user"""
    try:
        username = InputValidator.validate_username(user_data.username)
        email = InputValidator.validate_email(user_data.email)
        password = InputValidator.validate_password(user_data.password)
    except ValidationException as e:
        raise app_exception_to_http_exception(e)
    
    existing_user = await UserController.get_user_by_username(db, username)
    if existing_user:
        logger.warning(f"Registration attempt with existing username: {username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    try:
        user = await UserController.create_user(
            db=db,
            username=username,
            email=email,
            password=password,
            role=UserRole.USER
        )
        
        return {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "message": "User registered successfully"
        }
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@auth_router.post("/login", response_model=LoginResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    response: Response,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
):
    """Login with username and password"""
    try:
        username = InputValidator.validate_username(login_data.username)
    except ValidationException as e:
        raise app_exception_to_http_exception(e)
    
    user = await UserController.authenticate_user(
        db=db,
        username=username,
        password=login_data.password
    )
    
    if not user:
        logger.warning(f"Failed login attempt: {username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role.value},
        settings=settings
    )
    
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=settings.ENV == "production",
        samesite="lax",
        max_age=settings.JWT_EXPIRATION_HOURS * 3600
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id
    }

@auth_router.post("/change-password", status_code=200)
@limiter.limit("5/minute")
async def change_password(
    request: Request,
    password_data: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(lambda: {})
):
    """Change user password"""
    from helpers.jwt_handler import verify_token
    
    try:
        verified_token = await verify_token(request)
        user_id = verified_token.get("user_id")
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    success = await UserController.change_password(
        db=db,
        user_id=user_id,
        old_password=password_data.old_password,
        new_password=password_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password change failed"
        )
    
    return {"message": "Password changed successfully"}