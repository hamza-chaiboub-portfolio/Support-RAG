"""Chunk model for managing data chunks and embeddings"""

from typing import Optional


class ChunkModel:
    """Chunk model for database operations"""
    
    def __init__(self, db_client=None):
        self.db_client = db_client
    
    @classmethod
    async def create_instance(cls, db_client=None):
        """Factory method to create model instance"""
        return cls(db_client=db_client)