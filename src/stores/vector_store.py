"""Vector database management using ChromeDB for document embeddings and retrieval"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import json


class VectorStore:
    """Manages vector storage and retrieval using ChromeDB"""
    
    def __init__(self, persist_directory: Optional[str] = None):
        """
        Initialize ChromeDB vector store
        
        Args:
            persist_directory: Directory to persist ChromeDB data. 
                              Defaults to ./chroma_data
        """
        try:
            import chromadb
        except ImportError:
            raise ImportError(
                "chromadb is not installed. "
                "Run: pip install chromadb"
            )
        
        self.chromadb = chromadb
        
        if persist_directory is None:
            persist_directory = str(Path.cwd() / "chroma_data")
        
        os.makedirs(persist_directory, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(
        self, 
        documents: List[str],
        ids: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        embeddings: Optional[List[List[float]]] = None
    ) -> None:
        """
        Add documents to the vector store
        
        Args:
            documents: List of document texts
            ids: List of unique document IDs
            metadatas: Optional list of metadata dicts per document
            embeddings: Optional pre-computed embeddings
        """
        if len(documents) != len(ids):
            raise ValueError("Documents and IDs must have same length")
        
        if metadatas and len(metadatas) != len(documents):
            raise ValueError("Metadatas and documents must have same length")
        
        try:
            if embeddings:
                self.collection.add(
                    documents=documents,
                    ids=ids,
                    metadatas=metadatas or [{} for _ in documents],
                    embeddings=embeddings
                )
            else:
                self.collection.add(
                    documents=documents,
                    ids=ids,
                    metadatas=metadatas or [{} for _ in documents]
                )
        except Exception as e:
            raise RuntimeError(f"Failed to add documents: {e}")
    
    def query(
        self,
        query_text: Optional[str] = None,
        query_embedding: Optional[List[float]] = None,
        n_results: int = 5,
        where: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Query the vector store
        
        Args:
            query_text: Text query for similarity search
            query_embedding: Pre-computed query embedding
            n_results: Number of results to return
            where: Optional metadata filter
        
        Returns:
            Query results with documents, metadatas, and distances
        """
        if query_text is None and query_embedding is None:
            raise ValueError("Either query_text or query_embedding must be provided")
        
        try:
            if query_text:
                results = self.collection.query(
                    query_texts=[query_text],
                    n_results=n_results,
                    where=where
                )
            else:
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results,
                    where=where
                )
            return results
        except Exception as e:
            raise RuntimeError(f"Failed to query vector store: {e}")
    
    def delete_documents(self, ids: List[str]) -> None:
        """
        Delete documents from the vector store
        
        Args:
            ids: List of document IDs to delete
        """
        try:
            self.collection.delete(ids=ids)
        except Exception as e:
            raise RuntimeError(f"Failed to delete documents: {e}")
    
    def update_documents(
        self,
        documents: List[str],
        ids: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        embeddings: Optional[List[List[float]]] = None
    ) -> None:
        """
        Update existing documents in the vector store
        
        Args:
            documents: List of updated document texts
            ids: List of document IDs to update
            metadatas: Optional updated metadatas
            embeddings: Optional pre-computed embeddings
        """
        if len(documents) != len(ids):
            raise ValueError("Documents and IDs must have same length")
        
        try:
            if embeddings:
                self.collection.update(
                    documents=documents,
                    ids=ids,
                    metadatas=metadatas or [{} for _ in documents],
                    embeddings=embeddings
                )
            else:
                self.collection.update(
                    documents=documents,
                    ids=ids,
                    metadatas=metadatas or [{} for _ in documents]
                )
        except Exception as e:
            raise RuntimeError(f"Failed to update documents: {e}")
    
    def count(self) -> int:
        """Get total number of documents in collection"""
        try:
            return self.collection.count()
        except Exception as e:
            raise RuntimeError(f"Failed to count documents: {e}")
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection"""
        return {
            "name": self.collection.name,
            "count": self.count(),
            "metadata": self.collection.metadata
        }
