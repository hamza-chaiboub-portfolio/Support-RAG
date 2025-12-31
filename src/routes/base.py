from fastapi import APIRouter, Depends
from pydantic import BaseModel

# Absolute imports using package structure
try:
    from helpers.config import get_settings, Settings
    from helpers.jwt_handler import get_current_user
    from helpers.auth import get_current_user_or_api_key
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from helpers.config import get_settings, Settings
    from helpers.jwt_handler import get_current_user
    from helpers.auth import get_current_user_or_api_key

base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],
)


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


@base_router.post("/predict", response_model=PredictResponse)
async def predict(
    request: PredictRequest,
    current_user: dict = Depends(get_current_user_or_api_key)
):
    return {"prediction": f"Processed text: {request.text}"}


@base_router.get("/metrics")
async def get_metrics(current_user: dict = Depends(get_current_user_or_api_key)):
    return {
        "metrics": {
            "requests_total": 0,
            "requests_latency_seconds": 0.0,
            "status": "metrics_endpoint"
        }
    }