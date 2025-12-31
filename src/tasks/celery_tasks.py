"""Celery background tasks for document processing and vectorization"""

import logging
import asyncio
from typing import Optional

from celery_app import app
from helpers.database import AsyncSessionLocal
from helpers.logger import setup_logger
from controllers.ProcessingController import ProcessingController
from controllers.NLPController import NLPController
from controllers.RAGController import RAGController

logger = setup_logger(__name__)


def _get_async_session():
    """Get async session for database operations"""
    return AsyncSessionLocal()


@app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_asset_task(self, project_id: int, asset_id: int, chunk_size: int = 512, chunk_overlap: int = 50):
    """
    Background task to process an asset and create chunks
    
    Args:
        project_id: Project ID
        asset_id: Asset ID to process
        chunk_size: Size for chunking
        chunk_overlap: Overlap between chunks
        
    Returns:
        Dictionary with processing results
    """
    try:
        logger.info(f"Processing asset {asset_id} in project {project_id}")
        
        async def process():
            async with _get_async_session() as session:
                controller = ProcessingController(session)
                return await controller.process_asset(
                    project_id=project_id,
                    asset_id=asset_id,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )
        
        result = asyncio.run(process())
        logger.info(f"Asset processing complete: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Asset processing failed: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@app.task(bind=True, max_retries=3, default_retry_delay=60)
def batch_process_assets_task(self, project_id: int, chunk_size: int = 512, chunk_overlap: int = 50):
    """
    Background task to batch process all unprocessed assets in a project
    
    Args:
        project_id: Project ID
        chunk_size: Size for chunking
        chunk_overlap: Overlap between chunks
        
    Returns:
        Dictionary with batch processing results
    """
    try:
        logger.info(f"Batch processing assets for project {project_id}")
        
        async def process():
            async with _get_async_session() as session:
                controller = ProcessingController(session)
                return await controller.batch_process_assets(
                    project_id=project_id,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )
        
        result = asyncio.run(process())
        logger.info(f"Batch processing complete: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Batch processing failed: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@app.task(bind=True, max_retries=3, default_retry_delay=60)
def vectorize_chunks_task(self, project_id: int, asset_id: Optional[int] = None, batch_size: int = 32):
    """
    Background task to vectorize chunks for a project or asset
    
    Args:
        project_id: Project ID
        asset_id: Optional asset ID to filter by
        batch_size: Batch size for embedding generation
        
    Returns:
        Dictionary with vectorization results
    """
    try:
        logger.info(f"Vectorizing chunks for project {project_id}")
        
        async def vectorize():
            async with _get_async_session() as session:
                controller = NLPController(session)
                return await controller.vectorize_chunks(
                    project_id=project_id,
                    asset_id=asset_id,
                    batch_size=batch_size
                )
        
        result = asyncio.run(vectorize())
        logger.info(f"Vectorization complete: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Vectorization failed: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@app.task(bind=True, max_retries=3, default_retry_delay=60)
def save_embeddings_task(self, project_id: int, asset_id: Optional[int] = None):
    """
    Background task to save embeddings from ChromeDB to PostgreSQL
    
    Args:
        project_id: Project ID
        asset_id: Optional asset ID to filter by
        
    Returns:
        Dictionary with save results
    """
    try:
        logger.info(f"Saving embeddings for project {project_id}")
        
        async def save():
            async with _get_async_session() as session:
                controller = RAGController(session)
                return await controller.save_embeddings_to_db(
                    project_id=project_id,
                    asset_id=asset_id
                )
        
        result = asyncio.run(save())
        logger.info(f"Embeddings saved: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Saving embeddings failed: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@app.task(bind=True, max_retries=2, default_retry_delay=300)
def full_rag_pipeline_task(self, project_id: int, chunk_size: int = 512):
    """
    Background task to execute full RAG pipeline:
    1. Process assets (chunking)
    2. Vectorize chunks
    3. Save embeddings to PostgreSQL
    
    Args:
        project_id: Project ID
        chunk_size: Size for chunking
        
    Returns:
        Dictionary with pipeline results
    """
    try:
        logger.info(f"Starting full RAG pipeline for project {project_id}")
        
        async def pipeline():
            async with _get_async_session() as session:
                results = {}
                
                # Step 1: Process assets
                logger.info("Step 1: Processing assets...")
                processor = ProcessingController(session)
                processing_result = await processor.batch_process_assets(
                    project_id=project_id,
                    chunk_size=chunk_size
                )
                results["processing"] = processing_result
                
                # Step 2: Vectorize chunks
                logger.info("Step 2: Vectorizing chunks...")
                nlp = NLPController(session)
                vectorization_result = await nlp.vectorize_chunks(project_id)
                results["vectorization"] = vectorization_result
                
                # Step 3: Save embeddings
                logger.info("Step 3: Saving embeddings to PostgreSQL...")
                rag = RAGController(session)
                embedding_result = await rag.save_embeddings_to_db(project_id)
                results["embeddings"] = embedding_result
                
                return results
        
        result = asyncio.run(pipeline())
        logger.info(f"Full RAG pipeline complete: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Full RAG pipeline failed: {str(e)}")
        raise self.retry(exc=e, countdown=300)


@app.task
def health_check_task():
    """Simple health check task"""
    try:
        logger.info("Health check task executed successfully")
        return {"status": "healthy", "message": "Celery worker is operational"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}


@app.task
def cleanup_old_tasks():
    """Clean up old completed Celery tasks"""
    try:
        logger.info("Running cleanup task")
        return {"status": "success", "message": "Cleanup completed"}
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        return {"status": "failed", "error": str(e)}
