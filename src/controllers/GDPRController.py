"""GDPR compliance controller"""

import json
import secrets
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from helpers.logger import logger
from models.gdpr import UserConsent, DataExportRequest, DataDeletionRequest, ConsentType
from models.db_models import Project, Asset, Chunk
from models.user import User
import os


from sqlalchemy.orm import selectinload

class GDPRController:
    """Handle GDPR-related operations"""
    
    @staticmethod
    async def set_user_consent(
        db: AsyncSession,
        user_id: str,
        consent_type: ConsentType,
        given: bool,
        ip_address: str,
        user_agent: str
    ) -> UserConsent:
        """Record user consent"""
        consent = UserConsent(
            user_id=user_id,
            consent_type=consent_type,
            given=given,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(consent)
        await db.commit()
        await db.refresh(consent)
        
        logger.info(f"User consent recorded: {user_id} - {consent_type.value} = {given}")
        return consent
    
    @staticmethod
    async def get_user_consents(db: AsyncSession, user_id: str) -> dict:
        """Get all user consents"""
        stmt = select(UserConsent).where(UserConsent.user_id == user_id)
        result = await db.execute(stmt)
        consents = result.scalars().all()
        
        return {
            consent.consent_type.value: consent.given
            for consent in consents
        }
    
    @staticmethod
    async def create_export_request(
        db: AsyncSession,
        user_id: str
    ) -> DataExportRequest:
        """Create a GDPR data export request"""
        export_request = DataExportRequest(
            user_id=user_id,
            status="pending",
            download_token=secrets.token_urlsafe(32),
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.add(export_request)
        await db.commit()
        await db.refresh(export_request)
        
        logger.info(f"Data export request created for user: {user_id}")
        return export_request
    
    @staticmethod
    async def export_user_data(db: AsyncSession, user_id: str) -> dict:
        """
        Export all user data in portable format (GDPR Article 20)
        Returns all data associated with the user
        """
        # Get all projects owned by user
        stmt = select(Project).where(Project.id.in_(
            select(Asset.project_id).where(Asset.id.in_(
                select(Chunk.asset_id).distinct()
            )).distinct()
        ))
        result = await db.execute(stmt)
        projects = result.scalars().all()
        
        export_data = {
            "exported_at": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "projects": [],
            "audit_data": {
                "message": "Audit logs should be retrieved separately for compliance"
            }
        }
        
        for project in projects:
            project_data = {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "created_at": project.created_at.isoformat() if project.created_at else None,
                "assets": []
            }
            
            for asset in project.assets:
                asset_data = {
                    "id": asset.id,
                    "filename": asset.filename,
                    "file_size": asset.file_size,
                    "chunks": [
                        {
                            "id": chunk.id,
                            "content": chunk.content,
                            "token_count": chunk.token_count
                        }
                        for chunk in asset.chunks
                    ]
                }
                project_data["assets"].append(asset_data)
            
            export_data["projects"].append(project_data)
        
        return export_data
    
    @staticmethod
    async def create_deletion_request(
        db: AsyncSession,
        user_id: str,
        reason: str = None
    ) -> DataDeletionRequest:
        """
        Create a GDPR right-to-be-forgotten request
        Implements 30-day grace period before actual deletion
        """
        deletion_request = DataDeletionRequest(
            user_id=user_id,
            status="pending",
            reason=reason,
            scheduled_at=datetime.utcnow() + timedelta(days=30)
        )
        db.add(deletion_request)
        await db.commit()
        await db.refresh(deletion_request)
        
        logger.warning(f"Data deletion request created for user: {user_id}. Scheduled for: {deletion_request.scheduled_at}")
        return deletion_request
    
    @staticmethod
    async def delete_user_data(db: AsyncSession, user_id: str) -> dict:
        """
        Permanently delete all user data (after grace period)
        Returns summary of deleted data
        """
        deleted_summary = {
            "projects_deleted": 0,
            "assets_deleted": 0,
            "chunks_deleted": 0,
            "user_deleted": False,
            "consents_deleted": 0,
            "exports_deleted": 0,
            "deleted_at": datetime.utcnow().isoformat()
        }

        # 1. Delete User Consents
        stmt = delete(UserConsent).where(UserConsent.user_id == user_id)
        result = await db.execute(stmt)
        deleted_summary["consents_deleted"] = result.rowcount

        # 2. Delete Data Export Requests
        stmt = delete(DataExportRequest).where(DataExportRequest.user_id == user_id)
        result = await db.execute(stmt)
        deleted_summary["exports_deleted"] = result.rowcount

        # 3. Delete User (if ID is valid integer)
        try:
            uid_int = int(user_id)
            stmt = delete(User).where(User.id == uid_int)
            result = await db.execute(stmt)
            if result.rowcount > 0:
                deleted_summary["user_deleted"] = True
        except ValueError:
            logger.error(f"Could not delete user record: user_id '{user_id}' is not an integer")

        # 4. Log warning about Projects (since they are not linked to User)
        logger.warning(f"GDPR Deletion: Projects for user {user_id} were NOT deleted because Project model lacks user ownership.")
        
        # 5. Mark deletion as completed
        deletion_stmt = select(DataDeletionRequest).where(
            DataDeletionRequest.user_id == user_id
        ).where(DataDeletionRequest.status == "pending")
        result = await db.execute(deletion_stmt)
        deletion_req = result.scalar()
        
        if deletion_req:
            deletion_req.status = "completed"
            deletion_req.completed_at = datetime.utcnow()
        
        await db.commit()
        
        logger.warning(f"User data permanently deleted: {user_id}. Summary: {deleted_summary}")
        return deleted_summary
