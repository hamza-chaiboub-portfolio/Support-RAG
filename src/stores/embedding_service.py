"""Embedding generation service for document vectorization"""

from typing import List, Optional, Union
import asyncio


class EmbeddingService:
    """Service for generating document embeddings"""
    
    _model_cache = {}
    
    def __init__(self, embedding_model: str = "sentence-transformers"):
        """
        Initialize embedding service
        
        Args:
            embedding_model: Type of embedding model to use
                           - "sentence-transformers": Local sentence transformers
                           - "openai": OpenAI embeddings API
        """
        self.embedding_model = embedding_model
        self.model = self._model_cache.get(embedding_model)
        if self.model is None:
            self._initialize_model()
            self._model_cache[embedding_model] = self.model
    
    def _initialize_model(self):
        """Initialize the embedding model"""
        if self.embedding_model == "sentence-transformers":
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(
                    "all-MiniLM-L6-v2"
                )
            except ImportError:
                raise ImportError(
                    "sentence-transformers not installed. "
                    "Run: pip install sentence-transformers"
                )
        
        elif self.embedding_model == "openai":
            try:
                from openai import OpenAI
                self.model = OpenAI()
            except ImportError:
                raise ImportError(
                    "openai not installed. "
                    "Run: pip install openai"
                )
    
    def embed_documents(
        self, 
        documents: List[str],
        batch_size: int = 32
    ) -> List[List[float]]:
        """
        Generate embeddings for a list of documents
        
        Args:
            documents: List of document texts to embed
            batch_size: Batch size for processing (only for sentence-transformers)
        
        Returns:
            List of embeddings (each embedding is a list of floats)
        """
        if not documents:
            return []
        
        if self.embedding_model == "sentence-transformers":
            try:
                embeddings = self.model.encode(
                    documents,
                    batch_size=batch_size,
                    convert_to_numpy=False
                )
                return [embedding.tolist() if hasattr(embedding, 'tolist') 
                        else embedding for embedding in embeddings]
            except Exception as e:
                raise RuntimeError(
                    f"Failed to embed documents with sentence-transformers: {e}"
                )
        
        elif self.embedding_model == "openai":
            try:
                embeddings = []
                for doc in documents:
                    response = self.model.embeddings.create(
                        input=doc,
                        model="text-embedding-3-small"
                    )
                    embeddings.append(response.data[0].embedding)
                return embeddings
            except Exception as e:
                raise RuntimeError(
                    f"Failed to embed documents with OpenAI: {e}"
                )
    
    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a single query
        
        Args:
            query: Query text to embed
        
        Returns:
            Query embedding as a list of floats
        """
        embeddings = self.embed_documents([query])
        return embeddings[0] if embeddings else []
    
    def get_model_info(self) -> dict:
        """Get information about the current embedding model"""
        if self.embedding_model == "sentence-transformers":
            return {
                "type": "sentence-transformers",
                "model": "all-MiniLM-L6-v2",
                "dimension": 384
            }
        elif self.embedding_model == "openai":
            return {
                "type": "openai",
                "model": "text-embedding-3-small",
                "dimension": 1536
            }
        return {"type": "unknown"}


class AsyncEmbeddingService(EmbeddingService):
    """Async version of EmbeddingService"""
    
    async def embed_documents_async(
        self,
        documents: List[str],
        batch_size: int = 32
    ) -> List[List[float]]:
        """
        Asynchronously generate embeddings for documents
        
        Args:
            documents: List of document texts
            batch_size: Batch size for processing
        
        Returns:
            List of embeddings
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.embed_documents,
            documents,
            batch_size
        )
    
    async def embed_query_async(self, query: str) -> List[float]:
        """
        Asynchronously generate embedding for a query
        
        Args:
            query: Query text
        
        Returns:
            Query embedding
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.embed_query,
            query
        )
