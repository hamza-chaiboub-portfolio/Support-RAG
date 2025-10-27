from fastapi import APIRouter, Depends, HTTPException, status
from helpers.config import get_settings, Settings
from helpers.jwt_handler import create_access_token, get_current_user
from pydantic import BaseModel

base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],
)


class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str

class PredictRequest(BaseModel):
    text: str

class PredictResponse(BaseModel):
    prediction: str

@base_router.get("/")
async def welcome(app_settings: Settings = Depends(get_settings)):
    return {
        "app_name": app_settings.APP_NAME,
        "app_version": app_settings.APP_VERSION,
    }

@base_router.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

@base_router.post("/auth/login", response_model=LoginResponse)
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

@base_router.post("/predict", response_model=PredictResponse)
async def predict(
    request: PredictRequest,
    current_user: dict = Depends(get_current_user)
):
    return {"prediction": f"Processed text: {request.text}"}

@base_router.get("/metrics")
async def get_metrics(current_user: dict = Depends(get_current_user)):
    return {
        "metrics": {
            "requests_total": 0,
            "requests_latency_seconds": 0.0,
            "status": "metrics_endpoint"
        }
    }