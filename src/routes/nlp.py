"""NLP and RAG routes for vectorization, search, and retrieval"""

import sys
from pathlib import Path
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from helpers.database import get_db
from helpers.exceptions import ResourceNotFoundException, ValidationException, DatabaseException
from helpers.jwt_handler import verify_token
from helpers.config import get_settings, Settings
from controllers.NLPController import NLPController
from schemas.chunk import VectorizationRequest, VectorizationResponse, VectorStoreInfoResponse
from schemas.search import SearchRequest, SearchResponse, RankingRequest, RankingResponse, RankedResult

logger = logging.getLogger('uvicorn.error')

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["nlp", "rag"],
)


@nlp_router.post(
    "/vectorize",
    response_model=VectorizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Vectorize document chunks",
    description="Vectorize all chunks for a project or specific asset using embeddings"
)
async def vectorize_chunks(
    request: VectorizationRequest,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Vectorize chunks and store embeddings in ChromeDB
    
    Args:
        request: Vectorization request with project and optional asset ID
        db: Database session
        token: JWT authentication token
        
    Returns:
        VectorizationResponse with status and results
        
    Raises:
        HTTPException: If project not found or operation fails
    """
    try:
        controller = NLPController(db)
        result = await controller.vectorize_chunks(
            project_id=request.project_id,
            asset_id=request.asset_id,
            batch_size=request.batch_size
        )
        
        return VectorizationResponse(**result)
        
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
        logger.error(f"Vectorization error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Vectorization failed"
        )


@nlp_router.post(
    "/search",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Semantic search",
    description="Search for chunks similar to a query using semantic similarity"
)
async def search_chunks(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Search for chunks similar to a query
    
    Args:
        request: Search request with query and filters
        db: Database session
        token: JWT authentication token
        
    Returns:
        SearchResponse with similar chunks and scores
        
    Raises:
        HTTPException: If search fails or inputs invalid
    """
    try:
        controller = NLPController(db)
        results = await controller.search_similar_chunks(
            project_id=request.project_id,
            query=request.query,
            n_results=request.n_results,
            threshold=request.threshold
        )
        
        return SearchResponse(
            query=request.query,
            project_id=request.project_id,
            total_results=len(results),
            results=results
        )
        
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
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed"
        )


@nlp_router.post(
    "/rank",
    response_model=RankingResponse,
    status_code=status.HTTP_200_OK,
    summary="Re-rank results",
    description="Re-rank documents based on relevance to a query"
)
async def rank_documents(
    request: RankingRequest,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Re-rank documents based on relevance
    
    Args:
        request: Ranking request with query and documents
        db: Database session
        token: JWT authentication token
        
    Returns:
        RankingResponse with ranked results
        
    Raises:
        HTTPException: If ranking fails
    """
    try:
        controller = NLPController(db)
        ranked = await controller.rerank_results(
            query=request.query,
            documents=request.documents,
            method=request.method
        )
        
        results = [
            RankedResult(
                rank=i + 1,
                document=doc,
                score=score
            )
            for i, (doc, score) in enumerate(ranked)
        ]
        
        return RankingResponse(
            query=request.query,
            total_documents=len(request.documents),
            results=results
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
        logger.error(f"Ranking error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ranking failed"
        )


@nlp_router.get(
    "/vector-store-info",
    response_model=VectorStoreInfoResponse,
    status_code=status.HTTP_200_OK,
    summary="Get vector store information",
    description="Get information about the vector store and embedding model"
)
async def get_vector_store_info(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Get vector store and embedding model information
    
    Args:
        db: Database session
        token: JWT authentication token
        
    Returns:
        VectorStoreInfoResponse with store and model info
    """
    try:
        controller = NLPController(db)
        info = controller.get_vector_store_info()
        
        return VectorStoreInfoResponse(**info)
        
    except Exception as e:
        logger.error(f"Vector store info error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve vector store information"
        )