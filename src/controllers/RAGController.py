"""RAG (Retrieval-Augmented Generation) controller combining retrieval and generation"""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from helpers.exceptions import (
    ResourceNotFoundException,
    ValidationException,
    DatabaseException,
)
from helpers.logger import setup_logger
from models.db_models import Chunk, Project
from repositories.project_repository import ProjectRepository
from controllers.NLPController import NLPController
from utils.llm_provider import LLMProviderFactory, BaseLLMProvider
from utils.document_processor import TokenCounter

logger = setup_logger(__name__)


class RAGController:
    """Controller for RAG operations combining search and generation"""
    
    def __init__(
        self,
        db: AsyncSession,
        llm_provider: Optional[BaseLLMProvider] = None,
        embedding_model: str = "sentence-transformers"
    ):
        """
        Initialize RAG controller
        
        Args:
            db: Database session
            llm_provider: LLM provider instance (optional)
            embedding_model: Embedding model type
        """
        self.db = db
        self.repo = ProjectRepository(db)
        self.logger = logger
        self.nlp_controller = NLPController(db, embedding_model)
        self.llm_provider = llm_provider
    
    async def rag_query(
        self,
        project_id: int,
        query: str,
        n_results: int = 5,
        threshold: float = 0.0,
        max_tokens: int = 512,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Execute RAG query: retrieve + generate
        
        Args:
            project_id: Project ID to search in
            query: Query text
            n_results: Number of retrieval results
            threshold: Similarity threshold
            max_tokens: Maximum tokens for generation
            temperature: Temperature for LLM
            
        Returns:
            Dictionary with retrieved chunks and generated response
            
        Raises:
            ResourceNotFoundException: If project not found
            ValidationException: If inputs invalid
            DatabaseException: If operation fails
        """
        try:
            # Verify project exists
            project = await self.repo.get_project(project_id)
            if not project:
                raise ResourceNotFoundException("Project", project_id)
            
            self.logger.info(f"Executing RAG query for project {project_id}: {query[:50]}...")
            
            # Retrieve similar chunks
            retrieved_chunks = await self.nlp_controller.search_similar_chunks(
                project_id=project_id,
                query=query,
                n_results=n_results,
                threshold=threshold
            )
            
            if not retrieved_chunks:
                self.logger.warning(f"No chunks retrieved for query: {query}")
                return {
                    "status": "success",
                    "project_id": project_id,
                    "query": query,
                    "retrieved_chunks": [],
                    "retrieved_count": 0,
                    "response": "No relevant information found.",
                    "generation_status": "no_context"
                }
            
            self.logger.info(f"Retrieved {len(retrieved_chunks)} chunks for RAG")
            
            # Extract chunk content for context
            context = [chunk["content"] for chunk in retrieved_chunks]
            
            # Generate response with context
            response = None
            generation_status = "skipped"
            
            if self.llm_provider:
                try:
                    self.logger.info("Generating response with LLM...")
                    response = await self.llm_provider.generate_with_context(
                        query=query,
                        context=context,
                        max_tokens=max_tokens,
                        temperature=temperature
                    )
                    generation_status = "success"
                    self.logger.info("Response generation complete")
                except Exception as e:
                    self.logger.error(f"Response generation failed: {str(e)}")
                    generation_status = "failed"
                    response = "Failed to generate response. Retrieved documents are available above."
            else:
                generation_status = "no_provider"
                response = "LLM provider not configured. Retrieved documents are available."
            
            return {
                "status": "success",
                "project_id": project_id,
                "query": query,
                "retrieved_chunks": retrieved_chunks,
                "retrieved_count": len(retrieved_chunks),
                "response": response,
                "generation_status": generation_status
            }
            
        except (ResourceNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"RAG query failed: {str(e)}")
            raise DatabaseException(f"RAG query failed: {str(e)}", operation="rag_query")
    
    async def save_embeddings_to_db(
        self,
        project_id: int,
        asset_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Save embeddings from ChromeDB to PostgreSQL vector column
        
        Args:
            project_id: Project ID
            asset_id: Optional asset ID to filter by
            
        Returns:
            Dictionary with save results
            
        Raises:
            ResourceNotFoundException: If project not found
            DatabaseException: If save fails
        """
        try:
            # Verify project exists
            project = await self.repo.get_project(project_id)
            if not project:
                raise ResourceNotFoundException("Project", project_id)
            
            self.logger.info(f"Saving embeddings to PostgreSQL for project {project_id}")
            
            # Get chunks to update
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
                    "chunks_updated": 0
                }
            
            self.logger.info(f"Generating embeddings for {len(chunks)} chunks...")
            
            # Generate embeddings
            chunk_contents = [chunk.content for chunk in chunks]
            embeddings = await self.nlp_controller.embedding_service.embed_documents_async(
                chunk_contents
            )
            
            # Update chunks with embeddings
            updated_count = 0
            for chunk, embedding in zip(chunks, embeddings):
                chunk.embedding_vector = embedding
                self.db.add(chunk)
                updated_count += 1
            
            await self.db.commit()
            
            self.logger.info(f"Updated {updated_count} chunks with embeddings")
            
            return {
                "status": "success",
                "project_id": project_id,
                "chunks_updated": updated_count,
                "embedding_dimension": len(embeddings[0]) if embeddings else 0
            }
            
        except ResourceNotFoundException:
            raise
        except Exception as e:
            self.logger.error(f"Failed to save embeddings: {str(e)}")
            raise DatabaseException(f"Failed to save embeddings: {str(e)}", operation="save_embeddings")
    
    async def get_rag_stats(self, project_id: int) -> Dict[str, Any]:
        """
        Get RAG pipeline statistics for a project
        
        Args:
            project_id: Project ID
            
        Returns:
            Dictionary with RAG statistics
            
        Raises:
            ResourceNotFoundException: If project not found
            DatabaseException: If retrieval fails
        """
        try:
            # Verify project exists
            project = await self.repo.get_project(project_id)
            if not project:
                raise ResourceNotFoundException("Project", project_id)
            
            # Get chunk statistics
            chunks_result = await self.db.execute(
                select(Chunk).where(Chunk.project_id == project_id)
            )
            chunks = chunks_result.scalars().all()
            
            # Count chunks with embeddings
            chunks_with_embeddings = sum(1 for c in chunks if c.embedding_vector is not None)
            chunks_vectorized_in_chromadb = self.nlp_controller.vector_store.count()
            
            total_tokens = sum(c.token_count or 0 for c in chunks)
            
            return {
                "project_id": project_id,
                "project_name": project.name,
                "total_chunks": len(chunks),
                "chunks_with_embeddings": chunks_with_embeddings,
                "chunks_vectorized_chromadb": chunks_vectorized_in_chromadb,
                "total_tokens": total_tokens,
                "avg_tokens_per_chunk": total_tokens // len(chunks) if chunks else 0,
                "vector_store_info": self.nlp_controller.get_vector_store_info()
            }
            
        except ResourceNotFoundException:
            raise
        except Exception as e:
            self.logger.error(f"Failed to get RAG stats: {str(e)}")
            raise DatabaseException(f"Failed to retrieve statistics: {str(e)}", operation="get_stats")
