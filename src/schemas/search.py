"""Pydantic schemas for search and retrieval requests and responses"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class SearchRequest(BaseModel):
    """Schema for semantic search request"""
    project_id: int = Field(..., description="Project ID to search in")
    query: str = Field(..., min_length=1, max_length=5000, description="Search query text")
    n_results: int = Field(5, ge=1, le=50, description="Number of results to return")
    threshold: float = Field(0.0, ge=0.0, le=1.0, description="Minimum similarity threshold")
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": 1,
                "query": "How do I reset my password?",
                "n_results": 5,
                "threshold": 0.3
            }
        }


class SimilarChunk(BaseModel):
    """Schema for a similar chunk in search results"""
    chunk_id: int = Field(..., description="Chunk ID")
    asset_id: int = Field(..., description="Asset ID")
    project_id: int = Field(..., description="Project ID")
    content: str = Field(..., description="Chunk content")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    metadata: Dict[str, Any] = Field(..., description="Chunk metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "chunk_id": 1,
                "asset_id": 1,
                "project_id": 1,
                "content": "To reset your password, go to the login page and click 'Forgot Password'...",
                "similarity_score": 0.8543,
                "metadata": {
                    "chunk_id": 1,
                    "asset_id": 1,
                    "project_id": 1,
                    "chunk_index": 0,
                    "token_count": 150
                }
            }
        }


class SearchResponse(BaseModel):
    """Schema for search response"""
    query: str = Field(..., description="Original search query")
    project_id: int = Field(..., description="Project ID searched")
    total_results: int = Field(..., description="Total number of results returned")
    results: List[SimilarChunk] = Field(..., description="List of similar chunks")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "How do I reset my password?",
                "project_id": 1,
                "total_results": 3,
                "results": [
                    {
                        "chunk_id": 1,
                        "asset_id": 1,
                        "project_id": 1,
                        "content": "To reset your password...",
                        "similarity_score": 0.8543,
                        "metadata": {}
                    }
                ]
            }
        }


class RankingRequest(BaseModel):
    """Schema for result re-ranking request"""
    query: str = Field(..., min_length=1, description="Query text")
    documents: List[str] = Field(..., min_items=1, description="Documents to rank")
    method: str = Field("similarity", description="Ranking method (similarity, bm25, etc.)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "How do I reset my password?",
                "documents": [
                    "Document 1 content...",
                    "Document 2 content...",
                    "Document 3 content..."
                ],
                "method": "similarity"
            }
        }


class RankedResult(BaseModel):
    """Schema for a ranked result"""
    rank: int = Field(..., ge=1, description="Rank position")
    document: str = Field(..., description="Document content")
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    
    class Config:
        json_schema_extra = {
            "example": {
                "rank": 1,
                "document": "To reset your password...",
                "score": 0.9234
            }
        }


class RankingResponse(BaseModel):
    """Schema for re-ranking response"""
    query: str = Field(..., description="Original query")
    total_documents: int = Field(..., description="Total documents ranked")
    results: List[RankedResult] = Field(..., description="Ranked results")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "How do I reset my password?",
                "total_documents": 3,
                "results": [
                    {
                        "rank": 1,
                        "document": "Document 1 content...",
                        "score": 0.9234
                    },
                    {
                        "rank": 2,
                        "document": "Document 2 content...",
                        "score": 0.8123
                    }
                ]
            }
        }
