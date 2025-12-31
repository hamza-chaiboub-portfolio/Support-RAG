from celery import shared_task
from helpers.database import AsyncSessionLocal
from controllers.GDPRController import GDPRController
from models.gdpr import DataDeletionRequest
from sqlalchemy import select
from datetime import datetime
from helpers.logger import logger
import asyncio

@shared_task(name="tasks.process_gdpr_deletions")
def process_gdpr_deletions():
    """
    Background task to process pending GDPR deletion requests.
    Finds requests where scheduled_at <= now and executes deletion.
    """
    async def _process():
        try:
            async with AsyncSessionLocal() as db:
                logger.info("Starting GDPR deletion task")
                
                # Find pending requests that are due
                stmt = select(DataDeletionRequest).where(
                    DataDeletionRequest.status == "pending",
                    DataDeletionRequest.scheduled_at <= datetime.utcnow()
                )
                result = await db.execute(stmt)
                requests = result.scalars().all()
                
                logger.info(f"Found {len(requests)} pending deletion requests")
                
                for req in requests:
                    try:
                        logger.info(f"Processing deletion for user {req.user_id}")
                        await GDPRController.delete_user_data(db, req.user_id)
                    except Exception as e:
                        logger.error(f"Error processing deletion for user {req.user_id}: {e}")
                
                logger.info("GDPR deletion task completed")
        except Exception as e:
            logger.error(f"Critical error in GDPR deletion task execution: {e}")

    # Run async code in sync Celery task
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    loop.run_until_complete(_process())
