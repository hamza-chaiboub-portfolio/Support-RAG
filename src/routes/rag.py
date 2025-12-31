"""Routes for RAG (Retrieval-Augmented Generation) operations"""

import sys
from pathlib import Path
import logging
import os

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from helpers.database import get_db
from helpers.exceptions import ResourceNotFoundException, ValidationException, DatabaseException
from helpers.jwt_handler import verify_token
from helpers.config import get_settings
from controllers.RAGController import RAGController
from utils.llm_provider import LLMProviderFactory

logger = logging.getLogger('uvicorn.error')

rag_router = APIRouter(
    prefix="/api/v1/rag",
    tags=["rag"],
)


class RAGQueryRequest(BaseModel):
    """Request schema for RAG query"""
    project_id: int = Field(..., description="Project ID")
    query: str = Field(..., min_length=1, max_length=5000, description="Query text")
    n_results: int = Field(5, ge=1, le=50, description="Number of retrieval results")
    threshold: float = Field(0.0, ge=0.0, le=1.0, description="Similarity threshold")
    max_tokens: int = Field(512, ge=50, le=2000, description="Max tokens for generation")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Temperature for generation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": 1,
                "query": "How do I reset my password?",
                "n_results": 5,
                "threshold": 0.3,
                "max_tokens": 512,
                "temperature": 0.7
            }
        }


class RAGChunk(BaseModel):
    """Retrieved chunk in RAG response"""
    chunk_id: int
    asset_id: int
    content: str
    similarity_score: float
    metadata: Dict[str, Any]


class RAGQueryResponse(BaseModel):
    """Response schema for RAG query"""
    status: str
    project_id: int
    query: str
    retrieved_chunks: List[RAGChunk]
    retrieved_count: int
    response: str
    generation_status: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "project_id": 1,
                "query": "How do I reset my password?",
                "retrieved_chunks": [
                    {
                        "chunk_id": 1,
                        "asset_id": 1,
                        "content": "To reset your password...",
                        "similarity_score": 0.85,
                        "metadata": {}
                    }
                ],
                "retrieved_count": 5,
                "response": "Based on the provided documentation...",
                "generation_status": "success"
            }
        }


class SaveEmbeddingsRequest(BaseModel):
    """Request schema for saving embeddings"""
    project_id: int = Field(..., description="Project ID")
    asset_id: Optional[int] = Field(None, description="Optional asset ID to filter by")
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": 1,
                "asset_id": None
            }
        }


class SaveEmbeddingsResponse(BaseModel):
    """Response schema for saving embeddings"""
    status: str
    project_id: int
    chunks_updated: int
    embedding_dimension: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "project_id": 1,
                "chunks_updated": 25,
                "embedding_dimension": 384
            }
        }


class RAGStats(BaseModel):
    """RAG pipeline statistics"""
    project_id: int
    project_name: str
    total_chunks: int
    chunks_with_embeddings: int
    chunks_vectorized_chromadb: int
    total_tokens: int
    avg_tokens_per_chunk: int
    vector_store_info: Dict[str, Any]


def _get_llm_provider(settings):
    """Get LLM provider from settings"""
    try:
        provider_type = settings.LLM_PROVIDER or "mock"
        api_key = settings.LLM_API_KEY
        base_url = getattr(settings, "LLM_BASE_URL", None)
        model = getattr(settings, "LLM_MODEL", None)
        
        if provider_type.lower() == "mock":
            from utils.llm_provider import MockLLMProvider
            return MockLLMProvider()
        else:
            kwargs = {}
            if base_url:
                kwargs["base_url"] = base_url
            if model:
                kwargs["model"] = model
                
            return LLMProviderFactory.create_provider(
                provider_type,
                api_key=api_key,
                **kwargs
            )
    except Exception as e:
        logger.warning(f"Failed to initialize LLM provider: {str(e)}, using mock")
        from utils.llm_provider import MockLLMProvider
        return MockLLMProvider()


@rag_router.post(
    "/query",
    response_model=RAGQueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute RAG query",
    description="Execute a RAG query with retrieval and generation"
)
async def execute_rag_query(
    request: RAGQueryRequest,
    db: AsyncSession = Depends(get_db),
    settings = Depends(get_settings),
    token: str = Depends(verify_token)
):
    """
    Execute RAG query: retrieve context and generate response
    
    Args:
        request: RAG query request
        db: Database session
        settings: App settings
        token: JWT authentication token
        
    Returns:
        RAGQueryResponse with retrieved chunks and generated response
        
    Raises:
        HTTPException: If query fails
    """
    try:
        # Get LLM provider
        llm_provider = _get_llm_provider(settings)
        
        # Initialize RAG controller
        controller = RAGController(db, llm_provider=llm_provider)
        
        # Execute RAG query
        result = await controller.rag_query(
            project_id=request.project_id,
            query=request.query,
            n_results=request.n_results,
            threshold=request.threshold,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        return RAGQueryResponse(**result)
        
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
        logger.error(f"RAG query error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="RAG query failed"
        )


@rag_router.post(
    "/save-embeddings",
    response_model=SaveEmbeddingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Save embeddings to PostgreSQL",
    description="Save embeddings from ChromeDB to PostgreSQL vector column"
)
async def save_embeddings_to_db(
    request: SaveEmbeddingsRequest,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Save embeddings to PostgreSQL vector column
    
    Args:
        request: Save embeddings request
        db: Database session
        token: JWT authentication token
        
    Returns:
        SaveEmbeddingsResponse with results
        
    Raises:
        HTTPException: If operation fails
    """
    try:
        controller = RAGController(db)
        result = await controller.save_embeddings_to_db(
            project_id=request.project_id,
            asset_id=request.asset_id
        )
        
        return SaveEmbeddingsResponse(**result)
        
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
        logger.error(f"Save embeddings error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save embeddings"
        )


@rag_router.get(
    "/stats",
    response_model=RAGStats,
    status_code=status.HTTP_200_OK,
    summary="Get RAG pipeline statistics",
    description="Get statistics about RAG pipeline for a project"
)
async def get_rag_statistics(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Get RAG pipeline statistics
    
    Args:
        project_id: Project ID
        db: Database session
        token: JWT authentication token
        
    Returns:
        RAGStats with pipeline statistics
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        controller = RAGController(db)
        stats = await controller.get_rag_stats(project_id)
        
        return RAGStats(**stats)
        
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
