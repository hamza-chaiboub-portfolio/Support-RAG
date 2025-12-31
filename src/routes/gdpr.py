"""GDPR compliance routes"""

import sys
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import json
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from helpers.database import get_db
from helpers.jwt_handler import verify_token
from helpers.limiter import limiter
from helpers.logger import logger
from helpers.validation import InputValidator
from helpers.exceptions import app_exception_to_http_exception, ValidationException
from controllers.GDPRController import GDPRController
from models.gdpr import ConsentType

gdpr_router = APIRouter(
    prefix="/api/v1/gdpr",
    tags=["gdpr"],
)


class ConsentRequest(BaseModel):
    """Request to set user consent"""
    consent_type: str
    given: bool


class DataDeletionRequest(BaseModel):
    """Request to delete user data"""
    reason: str = None


class ExportResponse(BaseModel):
    """Response for data export"""
    status: str
    download_token: str
    expires_at: str
    message: str


@gdpr_router.post("/consent", status_code=201)
@limiter.limit("10/minute")
async def set_consent(
    request: Request,
    consent_data: ConsentRequest,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token)
):
    """Set user consent for data processing"""
    try:
        consent_type_str = InputValidator.validate_string_field(
            consent_data.consent_type,
            "consent_type",
            min_length=1,
            max_length=50
        )
        
        user_id = token.get("sub")
        consent_type = ConsentType(consent_type_str)
        
        consent = await GDPRController.set_user_consent(
            db=db,
            user_id=user_id,
            consent_type=consent_type,
            given=consent_data.given,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", "unknown")
        )
        
        return {
            "status": "success",
            "consent_type": consent.consent_type.value,
            "given": consent.given,
            "recorded_at": consent.created_at.isoformat()
        }
    except ValidationException as e:
        raise app_exception_to_http_exception(e)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid consent type"
        )


@gdpr_router.get("/consent")
@limiter.limit("30/minute")
async def get_consents(
    request: Request,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token)
):
    """Get all user consents"""
    user_id = token.get("sub")
    consents = await GDPRController.get_user_consents(db, user_id)
    
    return {
        "user_id": user_id,
        "consents": consents,
        "retrieved_at": datetime.utcnow().isoformat()
    }


@gdpr_router.post("/export", response_model=ExportResponse, status_code=202)
@limiter.limit("5/minute")
async def request_data_export(
    request: Request,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token)
):
    """
    Request GDPR data export (Right of Data Portability - Article 20)
    Returns portable data format for user
    """
    user_id = token.get("sub")
    
    export_req = await GDPRController.create_export_request(db, user_id)
    
    # Note: In production, this would be handled by async task
    # For now, we export immediately
    export_data = await GDPRController.export_user_data(db, user_id)
    
    logger.info(f"Data export generated for user: {user_id}")
    
    return {
        "status": "processing",
        "download_token": export_req.download_token,
        "expires_at": export_req.expires_at.isoformat(),
        "message": "Your data export will be available for 7 days. Use the download_token to retrieve it."
    }


@gdpr_router.post("/export/download/{token}")
@limiter.limit("10/minute")
async def download_export(
    request: Request,
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """Download exported user data"""
    from sqlalchemy import select
    
    stmt = select(DataExportRequest.__class__).where(
        DataExportRequest.download_token == token
    )
    result = await db.execute(stmt)
    export_req = result.scalar()
    
    if not export_req or datetime.utcnow() > export_req.expires_at:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export not found or expired"
        )
    
    export_data = await GDPRController.export_user_data(db, export_req.user_id)
    
    logger.info(f"User data downloaded: {export_req.user_id}")
    
    return {
        "data": export_data,
        "format": "json",
        "downloaded_at": datetime.utcnow().isoformat()
    }


@gdpr_router.post("/delete", status_code=202)
@limiter.limit("2/day")
async def request_data_deletion(
    request: Request,
    deletion_req: DataDeletionRequest,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token)
):
    """
    Request GDPR right to be forgotten (Article 17)
    Implements 30-day grace period before deletion
    """
    try:
        reason = None
        if deletion_req.reason:
            reason = InputValidator.validate_string_field(
                deletion_req.reason,
                "reason",
                min_length=1,
                max_length=500
            )
        
        user_id = token.get("sub")
        
        del_req = await GDPRController.create_deletion_request(
            db,
            user_id,
            reason
        )
        
        return {
            "status": "pending",
            "user_id": user_id,
            "requested_at": del_req.created_at.isoformat(),
            "scheduled_deletion": del_req.scheduled_at.isoformat(),
            "message": "Your deletion request has been received. Data will be permanently deleted in 30 days. You can cancel this request by contacting support within this period."
        }
    except ValidationException as e:
        raise app_exception_to_http_exception(e)


@gdpr_router.get("/status/deletion")
@limiter.limit("10/minute")
async def get_deletion_status(
    request: Request,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token)
):
    """Check status of data deletion request"""
    from sqlalchemy import select
    
    user_id = token.get("sub")
    
    stmt = select(DataDeletionRequest.__class__).where(
        DataDeletionRequest.user_id == user_id
    ).order_by(DataDeletionRequest.created_at.desc())
    
    result = await db.execute(stmt)
    del_req = result.scalar()
    
    if not del_req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No deletion request found"
        )
    
    return {
        "status": del_req.status,
        "requested_at": del_req.created_at.isoformat(),
        "scheduled_deletion": del_req.scheduled_at.isoformat() if del_req.scheduled_at else None,
        "completed_at": del_req.completed_at.isoformat() if del_req.completed_at else None
    }
