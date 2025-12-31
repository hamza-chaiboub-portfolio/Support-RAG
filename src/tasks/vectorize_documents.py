"""Task for vectorizing documents and storing them in ChromeDB"""

import asyncio
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from stores.vector_store import VectorStore
from stores.embedding_service import AsyncEmbeddingService
from models.db_models import Chunk, Asset, Project
from helpers.logger import get_logger


logger = get_logger(__name__)


class VectorizationTask:
    """Task for vectorizing documents from the database"""
    
    def __init__(
        self,
        embedding_model: str = "sentence-transformers",
        vector_store_dir: Optional[str] = None
    ):
        """
        Initialize vectorization task
        
        Args:
            embedding_model: Type of embedding model ("sentence-transformers" or "openai")
            vector_store_dir: Directory for ChromeDB persistence
        """
        self.embedding_service = AsyncEmbeddingService(embedding_model)
        self.vector_store = VectorStore(vector_store_dir)
        logger.info(f"Vectorization task initialized with {embedding_model}")
    
    async def vectorize_chunks(
        self,
        session: AsyncSession,
        project_id: Optional[int] = None,
        asset_id: Optional[int] = None,
        batch_size: int = 32
    ) -> dict:
        """
        Vectorize chunks from the database
        
        Args:
            session: Database session
            project_id: Optional project ID to filter by
            asset_id: Optional asset ID to filter by
            batch_size: Batch size for embedding generation
        
        Returns:
            Dictionary with vectorization results
        """
        logger.info(
            f"Starting vectorization: project_id={project_id}, asset_id={asset_id}"
        )
        
        query = select(Chunk)
        
        if project_id:
            query = query.where(Chunk.project_id == project_id)
        
        if asset_id:
            query = query.where(Chunk.asset_id == asset_id)
        
        result = await session.execute(query)
        chunks = result.scalars().all()
        
        if not chunks:
            logger.warning("No chunks found to vectorize")
            return {
                "status": "no_chunks",
                "chunks_processed": 0,
                "chunks_vectorized": 0
            }
        
        documents = [chunk.content for chunk in chunks]
        chunk_ids = [f"chunk_{chunk.id}" for chunk in chunks]
        
        logger.info(f"Embedding {len(documents)} chunks...")
        
        try:
            embeddings = await self.embedding_service.embed_documents_async(
                documents,
                batch_size=batch_size
            )
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            raise
        
        metadatas = [
            {
                "chunk_id": chunk.id,
                "asset_id": chunk.asset_id,
                "project_id": chunk.project_id,
                "chunk_index": chunk.chunk_index,
                "token_count": chunk.token_count or 0
            }
            for chunk in chunks
        ]
        
        logger.info(f"Adding {len(embeddings)} embeddings to vector store...")
        
        try:
            self.vector_store.add_documents(
                documents=documents,
                ids=chunk_ids,
                metadatas=metadatas,
                embeddings=embeddings
            )
        except Exception as e:
            logger.error(f"Failed to add documents to vector store: {e}")
            raise
        
        self.vector_store.persist()
        
        logger.info(
            f"Vectorization completed: {len(documents)} chunks processed, "
            f"{len(embeddings)} embeddings created"
        )
        
        return {
            "status": "success",
            "chunks_processed": len(chunks),
            "chunks_vectorized": len(embeddings),
            "embedding_dimension": len(embeddings[0]) if embeddings else 0
        }
    
    async def search_similar_chunks(
        self,
        query: str,
        project_id: Optional[int] = None,
        n_results: int = 5
    ) -> List[dict]:
        """
        Search for chunks similar to a query
        
        Args:
            query: Search query text
            project_id: Optional filter by project
            n_results: Number of results to return
        
        Returns:
            List of similar chunks with scores
        """
        logger.info(f"Searching for similar chunks: {query[:50]}...")
        
        try:
            query_embedding = await self.embedding_service.embed_query_async(query)
        except Exception as e:
            logger.error(f"Query embedding failed: {e}")
            raise
        
        where = None
        if project_id:
            where = {"project_id": {"$eq": project_id}}
        
        try:
            results = self.vector_store.query(
                query_embedding=query_embedding,
                n_results=n_results,
                where=where
            )
        except Exception as e:
            logger.error(f"Vector store query failed: {e}")
            raise
        
        similar_chunks = []
        
        if results and results.get("ids"):
            for i, chunk_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else 0
                document = results["documents"][0][i] if results["documents"] else ""
                
                similar_chunks.append({
                    "chunk_id": metadata.get("chunk_id"),
                    "asset_id": metadata.get("asset_id"),
                    "project_id": metadata.get("project_id"),
                    "content": document,
                    "similarity_score": 1 - distance,
                    "metadata": metadata
                })
        
        logger.info(f"Found {len(similar_chunks)} similar chunks")
        return similar_chunks
    
    def get_vector_store_info(self) -> dict:
        """Get information about the vector store"""
        return {
            "collection_info": self.vector_store.get_collection_info(),
            "embedding_model": self.embedding_service.get_model_info()
        }
