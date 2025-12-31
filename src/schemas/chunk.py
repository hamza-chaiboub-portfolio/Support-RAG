"""Pydantic schemas for Chunk-related requests and responses"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChunkCreateRequest(BaseModel):
    """Schema for creating a chunk"""
    project_id: int = Field(..., description="Project ID")
    asset_id: int = Field(..., description="Asset ID")
    content: str = Field(..., min_length=1, description="Chunk content text")
    chunk_index: int = Field(..., ge=0, description="Index of chunk within asset")
    token_count: Optional[int] = Field(None, description="Token count for chunk")
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": 1,
                "asset_id": 1,
                "content": "This is a text chunk extracted from a document...",
                "chunk_index": 0,
                "token_count": 150
            }
        }


class ChunkResponse(BaseModel):
    """Schema for chunk response"""
    id: int
    project_id: int
    asset_id: int
    content: str
    chunk_index: int
    token_count: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "project_id": 1,
                "asset_id": 1,
                "content": "This is a text chunk extracted from a document...",
                "chunk_index": 0,
                "token_count": 150,
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00"
            }
        }


class VectorizationRequest(BaseModel):
    """Schema for vectorization request"""
    project_id: int = Field(..., description="Project ID to vectorize")
    asset_id: Optional[int] = Field(None, description="Optional asset ID to filter by")
    batch_size: int = Field(32, ge=1, le=256, description="Batch size for embedding generation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": 1,
                "asset_id": None,
                "batch_size": 32
            }
        }


class VectorizationResponse(BaseModel):
    """Schema for vectorization response"""
    status: str = Field(..., description="Status of vectorization")
    project_id: int = Field(..., description="Project ID")
    chunks_processed: int = Field(..., description="Number of chunks processed")
    chunks_vectorized: int = Field(..., description="Number of chunks vectorized")
    embedding_dimension: Optional[int] = Field(None, description="Dimension of embeddings")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "project_id": 1,
                "chunks_processed": 25,
                "chunks_vectorized": 25,
                "embedding_dimension": 384
            }
        }


class VectorStoreInfoResponse(BaseModel):
    """Schema for vector store information response"""
    collection_info: Dict[str, Any] = Field(..., description="Collection information")
    embedding_model: Dict[str, Any] = Field(..., description="Embedding model information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "collection_info": {
                    "name": "documents",
                    "count": 100,
                    "metadata": {"hnsw:space": "cosine"}
                },
                "embedding_model": {
                    "type": "sentence-transformers",
                    "model": "all-MiniLM-L6-v2",
                    "dimension": 384
                }
            }
        }
