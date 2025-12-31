from pydantic import BaseModel, Field
from typing import Optional


class ProcessRequest(BaseModel):
    """Request schema for data processing endpoints"""
    
    file_id: str = Field(..., description="ID of the file to process")
    chunk_size: int = Field(default=512, description="Size of chunks for processing")
    overlap_size: int = Field(default=50, description="Overlap size between chunks")
    do_reset: bool = Field(default=False, description="Whether to reset processing state")
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_id": "file-12345",
                "chunk_size": 512,
                "overlap_size": 50,
                "do_reset": False
            }
        }