"""NLP and RAG controller for document vectorization and semantic search"""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from helpers.exceptions import (
    ResourceNotFoundException,
    ValidationException,
    DatabaseException,
)
from helpers.logger import setup_logger
from models.db_models import Chunk, Asset, Project
from stores.vector_store import VectorStore
from stores.embedding_service import AsyncEmbeddingService
from repositories.project_repository import ProjectRepository

logger = setup_logger(__name__)


class NLPController:
    """Controller for NLP and RAG operations"""
    
    def __init__(
        self,
        db: AsyncSession,
        embedding_model: str = "sentence-transformers",
        vector_store_dir: Optional[str] = None
    ):
        """
        Initialize NLP controller
        
        Args:
            db: Database session
            embedding_model: Type of embedding model ("sentence-transformers" or "openai")
            vector_store_dir: Directory for ChromeDB persistence
        """
        self.db = db
        self.repo = ProjectRepository(db)
        self.logger = logger
        self.embedding_service = AsyncEmbeddingService(embedding_model)
        self.vector_store = VectorStore(vector_store_dir)
    
    async def vectorize_chunks(
        self,
        project_id: int,
        asset_id: Optional[int] = None,
        batch_size: int = 32
    ) -> Dict[str, Any]:
        """
        Vectorize chunks from database and store in ChromeDB
        
        Args:
            project_id: Project ID to vectorize
            asset_id: Optional asset ID to filter by
            batch_size: Batch size for embedding generation
            
        Returns:
            Dictionary with vectorization results
            
        Raises:
            ResourceNotFoundException: If project/asset not found
            ValidationException: If validation fails
            DatabaseException: If database operation fails
        """
        try:
            # Verify project exists
            project = await self.repo.get_project(project_id)
            if not project:
                raise ResourceNotFoundException("Project", project_id)
            
            self.logger.info(f"Starting vectorization for project {project_id}")
            
            # Build query
            query = select(Chunk).where(Chunk.project_id == project_id)
            if asset_id:
                query = query.where(Chunk.asset_id == asset_id)
            
            result = await self.db.execute(query)
            chunks = result.scalars().all()
            
            if not chunks:
                self.logger.warning(f"No chunks found for project {project_id}")
                return {
                    "status": "no_chunks",
                    "project_id": project_id,
                    "chunks_processed": 0,
                    "chunks_vectorized": 0
                }
            
            # Extract documents and prepare metadata
            documents = [chunk.content for chunk in chunks]
            chunk_ids = [f"chunk_{chunk.id}" for chunk in chunks]
            
            self.logger.info(f"Embedding {len(documents)} chunks for project {project_id}")
            
            # Generate embeddings
            embeddings = await self.embedding_service.embed_documents_async(
                documents,
                batch_size=batch_size
            )
            
            # Prepare metadata
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
            
            # Add to vector store
            self.vector_store.add_documents(
                documents=documents,
                ids=chunk_ids,
                metadatas=metadatas,
                embeddings=embeddings
            )
            
            self.logger.info(
                f"Vectorization complete: {len(embeddings)} embeddings created for project {project_id}"
            )
            
            return {
                "status": "success",
                "project_id": project_id,
                "chunks_processed": len(chunks),
                "chunks_vectorized": len(embeddings),
                "embedding_dimension": len(embeddings[0]) if embeddings else 0
            }
            
        except ResourceNotFoundException:
            raise
        except Exception as e:
            self.logger.error(f"Vectorization failed for project {project_id}: {str(e)}")
            raise DatabaseException(f"Vectorization failed: {str(e)}", operation="vectorize")
    
    async def search_similar_chunks(
        self,
        project_id: int,
        query: str,
        n_results: int = 5,
        threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search for chunks similar to query using semantic search
        
        Args:
            project_id: Project ID to search in
            query: Query text for similarity search
            n_results: Number of results to return
            threshold: Minimum similarity threshold (0-1)
            
        Returns:
            List of similar chunks with metadata and scores
            
        Raises:
            ResourceNotFoundException: If project not found
            ValidationException: If validation fails
            DatabaseException: If search fails
        """
        try:
            # Validate inputs
            if not query or len(query.strip()) == 0:
                raise ValidationException("Query cannot be empty", field="query")
            
            if n_results < 1 or n_results > 50:
                n_results = 5
            
            # Verify project exists
            project = await self.repo.get_project(project_id)
            if not project:
                raise ResourceNotFoundException("Project", project_id)
            
            self.logger.info(f"Searching for: {query[:50]}... in project {project_id}")
            
            # Generate query embedding
            query_embedding = await self.embedding_service.embed_query_async(query)
            
            # Search vector store with project filter
            where_filter = {"project_id": {"$eq": project_id}}
            
            results = self.vector_store.query(
                query_embedding=query_embedding,
                n_results=n_results,
                where=where_filter
            )
            
            similar_chunks = []
            
            if results and results.get("ids"):
                for i, chunk_id in enumerate(results["ids"][0]):
                    metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                    distance = results["distances"][0][i] if results["distances"] else 0
                    document = results["documents"][0][i] if results["documents"] else ""
                    
                    similarity_score = 1 - distance
                    
                    # Apply threshold filtering
                    if similarity_score >= threshold:
                        similar_chunks.append({
                            "chunk_id": metadata.get("chunk_id"),
                            "asset_id": metadata.get("asset_id"),
                            "project_id": metadata.get("project_id"),
                            "content": document,
                            "similarity_score": round(similarity_score, 4),
                            "metadata": metadata
                        })
            
            self.logger.info(f"Search returned {len(similar_chunks)} results")
            return similar_chunks
            
        except (ResourceNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Search failed for project {project_id}: {str(e)}")
            raise DatabaseException(f"Search failed: {str(e)}", operation="search")
    
    async def rerank_results(
        self,
        query: str,
        documents: List[str],
        method: str = "similarity"
    ) -> List[tuple[str, float]]:
        """
        Re-rank search results based on relevance
        
        Args:
            query: Original query text
            documents: List of documents to rank
            method: Ranking method ("similarity", "bm25", etc.)
            
        Returns:
            List of (document, score) tuples sorted by relevance
            
        Raises:
            ValidationException: If inputs invalid
            DatabaseException: If ranking fails
        """
        try:
            if not documents:
                return []
            
            if method == "similarity":
                # Simple cosine similarity ranking
                query_embedding = await self.embedding_service.embed_query_async(query)
                doc_embeddings = await self.embedding_service.embed_documents_async(documents)
                
                # Calculate similarity scores
                import numpy as np
                scores = []
                query_vec = np.array(query_embedding)
                for doc_embedding in doc_embeddings:
                    doc_vec = np.array(doc_embedding)
                    similarity = np.dot(query_vec, doc_vec) / (
                        np.linalg.norm(query_vec) * np.linalg.norm(doc_vec) + 1e-10
                    )
                    scores.append(similarity)
                
                # Sort by score descending
                ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
                return ranked
            
            else:
                raise ValidationException(f"Unknown ranking method: {method}", field="method")
                
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Re-ranking failed: {str(e)}")
            raise DatabaseException(f"Re-ranking failed: {str(e)}", operation="rerank")
    
    def get_vector_store_info(self) -> Dict[str, Any]:
        """
        Get information about the vector store
        
        Returns:
            Dictionary with vector store and embedding model info
        """
        try:
            return {
                "collection_info": self.vector_store.get_collection_info(),
                "embedding_model": self.embedding_service.get_model_info()
            }
        except Exception as e:
            self.logger.error(f"Failed to get vector store info: {str(e)}")
            return {"error": str(e)}