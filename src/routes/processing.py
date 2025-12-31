"""Routes for document processing and chunking"""

import sys
from pathlib import Path
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from helpers.database import get_db
from helpers.exceptions import ResourceNotFoundException, ValidationException, DatabaseException
from helpers.jwt_handler import verify_token
from controllers.ProcessingController import ProcessingController
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

logger = logging.getLogger('uvicorn.error')

processing_router = APIRouter(
    prefix="/api/v1/processing",
    tags=["processing", "chunking"],
)


class ProcessAssetRequest(BaseModel):
    """Request schema for processing an asset"""
    project_id: int = Field(..., description="Project ID")
    asset_id: int = Field(..., description="Asset ID to process")
    chunk_size: int = Field(512, ge=50, le=2000, description="Chunk size in characters or tokens")
    chunk_overlap: int = Field(50, ge=0, le=500, description="Overlap between chunks")
    strategy: str = Field("size", description="Chunking strategy: size, tokens, sentences, paragraphs")
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": 1,
                "asset_id": 1,
                "chunk_size": 512,
                "chunk_overlap": 50,
                "strategy": "size"
            }
        }


class ProcessAssetResponse(BaseModel):
    """Response schema for asset processing"""
    status: str
    project_id: int
    asset_id: int
    asset_filename: str
    chunks_created: int
    total_tokens: int
    average_tokens_per_chunk: int
    chunk_ids: List[int]
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "project_id": 1,
                "asset_id": 1,
                "asset_filename": "document.pdf",
                "chunks_created": 25,
                "total_tokens": 12500,
                "average_tokens_per_chunk": 500,
                "chunk_ids": [1, 2, 3, 4, 5]
            }
        }


class BatchProcessRequest(BaseModel):
    """Request schema for batch processing"""
    project_id: int = Field(..., description="Project ID")
    chunk_size: int = Field(512, ge=50, le=2000)
    chunk_overlap: int = Field(50, ge=0, le=500)
    strategy: str = Field("size")


class BatchProcessResult(BaseModel):
    """Single result in batch processing"""
    status: str
    project_id: int
    asset_id: int
    asset_filename: str
    chunks_created: int
    total_tokens: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "project_id": 1,
                "asset_id": 1,
                "asset_filename": "document.pdf",
                "chunks_created": 25,
                "total_tokens": 12500
            }
        }


class BatchProcessResponse(BaseModel):
    """Response schema for batch processing"""
    status: str
    project_id: int
    total_assets: int
    processed_assets: int
    failed_assets: int
    results: List[BatchProcessResult]


class ChunkStats(BaseModel):
    """Chunk statistics"""
    project_id: int
    asset_id: Optional[int]
    total_chunks: int
    total_tokens: int
    avg_chunk_size: int
    min_chunk_size: int
    max_chunk_size: int
    avg_tokens_per_chunk: Optional[int] = None
    min_tokens: Optional[int] = None
    max_tokens: Optional[int] = None


@processing_router.post(
    "/process-asset",
    response_model=ProcessAssetResponse,
    status_code=status.HTTP_200_OK,
    summary="Process a single asset",
    description="Extract text from an asset and create chunks"
)
async def process_asset(
    request: ProcessAssetRequest,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Process a single asset and create chunks
    
    Args:
        request: Processing request
        db: Database session
        token: JWT authentication token
        
    Returns:
        ProcessAssetResponse with results
        
    Raises:
        HTTPException: If processing fails
    """
    try:
        controller = ProcessingController(db)
        result = await controller.process_asset(
            project_id=request.project_id,
            asset_id=request.asset_id,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
            strategy=request.strategy
        )
        
        return ProcessAssetResponse(**result)
        
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Asset processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Asset processing failed"
        )


@processing_router.post(
    "/batch-process",
    response_model=BatchProcessResponse,
    status_code=status.HTTP_200_OK,
    summary="Batch process assets",
    description="Process all unprocessed assets in a project"
)
async def batch_process_assets(
    request: BatchProcessRequest,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Batch process all unprocessed assets in a project
    
    Args:
        request: Batch processing request
        db: Database session
        token: JWT authentication token
        
    Returns:
        BatchProcessResponse with results
        
    Raises:
        HTTPException: If batch processing fails
    """
    try:
        controller = ProcessingController(db)
        result = await controller.batch_process_assets(
            project_id=request.project_id,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
            strategy=request.strategy
        )
        
        return BatchProcessResponse(
            status=result["status"],
            project_id=result["project_id"],
            total_assets=result["total_assets"],
            processed_assets=result["processed_assets"],
            failed_assets=result["failed_assets"],
            results=result["results"]
        )
        
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Batch processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Batch processing failed"
        )


@processing_router.get(
    "/chunk-stats",
    response_model=ChunkStats,
    status_code=status.HTTP_200_OK,
    summary="Get chunk statistics",
    description="Get statistics about chunks in a project or asset"
)
async def get_chunk_stats(
    project_id: int,
    asset_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Get chunk statistics
    
    Args:
        project_id: Project ID
        asset_id: Optional asset ID to filter by
        db: Database session
        token: JWT authentication token
        
    Returns:
        ChunkStats with statistics
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        controller = ProcessingController(db)
        stats = await controller.get_chunk_stats(
            project_id=project_id,
            asset_id=asset_id
        )
        
        return ChunkStats(**stats)
        
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Stats retrieval error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics"
        )
