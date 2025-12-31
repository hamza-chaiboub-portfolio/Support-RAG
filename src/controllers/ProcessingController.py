"""Document processing controller for chunking and preparing documents"""

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
from models.db_models import Asset, Chunk, Project
from repositories.project_repository import ProjectRepository
from utils.document_processor import (
    DocumentProcessor,
    ChunkingStrategy,
    TokenCounter
)

logger = setup_logger(__name__)


class ProcessingController:
    """Controller for document processing and chunking"""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize processing controller
        
        Args:
            db: Database session
        """
        self.db = db
        self.repo = ProjectRepository(db)
        self.logger = logger
        self.document_processor = DocumentProcessor()
    
    async def process_asset(
        self,
        project_id: int,
        asset_id: int,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        strategy: str = "size"
    ) -> Dict[str, Any]:
        """
        Process an asset and create chunks
        
        Args:
            project_id: Project ID
            asset_id: Asset ID to process
            chunk_size: Size for chunking (characters or tokens)
            chunk_overlap: Overlap between chunks
            strategy: Chunking strategy ("size", "tokens", "sentences", "paragraphs")
            
        Returns:
            Dictionary with processing results
            
        Raises:
            ResourceNotFoundException: If project or asset not found
            ValidationException: If validation fails
            DatabaseException: If database operation fails
        """
        try:
            # Verify project exists
            project = await self.repo.get_project(project_id)
            if not project:
                raise ResourceNotFoundException("Project", project_id)
            
            # Get asset
            asset_result = await self.db.execute(
                select(Asset).where(Asset.id == asset_id)
            )
            asset = asset_result.scalars().first()
            
            if not asset:
                raise ResourceNotFoundException("Asset", asset_id)
            
            self.logger.info(
                f"Processing asset {asset_id} from project {project_id} "
                f"with {strategy} strategy"
            )
            
            # Validate file exists
            if not asset.file_path or not __import__('os').path.exists(asset.file_path):
                raise ValidationException(
                    f"File not found: {asset.file_path}",
                    field="file_path"
                )
            
            # Extract text from document
            text = self.document_processor.extract_text(asset.file_path)
            
            if not text or len(text.strip()) == 0:
                raise ValidationException("No text extracted from document", field="content")
            
            self.logger.info(f"Extracted {len(text)} characters from asset {asset_id}")
            
            # Chunk text based on strategy
            chunks = self._chunk_text(text, strategy, chunk_size, chunk_overlap)
            
            if not chunks:
                raise ValidationException("No chunks generated from document", field="chunks")
            
            self.logger.info(f"Generated {len(chunks)} chunks for asset {asset_id}")
            
            # Store chunks in database
            stored_chunks = []
            for chunk_index, chunk_content in enumerate(chunks):
                token_count = TokenCounter.count_tokens(chunk_content)
                
                chunk = Chunk(
                    project_id=project_id,
                    asset_id=asset_id,
                    content=chunk_content,
                    chunk_index=chunk_index,
                    token_count=token_count
                )
                self.db.add(chunk)
                stored_chunks.append(chunk)
            
            # Commit all chunks
            await self.db.commit()
            
            # Refresh chunks to get IDs
            for chunk in stored_chunks:
                await self.db.refresh(chunk)
            
            # Mark asset as processed
            asset.is_processed = True
            self.db.add(asset)
            await self.db.commit()
            
            total_tokens = sum(c.token_count for c in stored_chunks)
            
            self.logger.info(
                f"Processing complete for asset {asset_id}: "
                f"{len(stored_chunks)} chunks, {total_tokens} total tokens"
            )
            
            return {
                "status": "success",
                "project_id": project_id,
                "asset_id": asset_id,
                "asset_filename": asset.filename,
                "chunks_created": len(stored_chunks),
                "total_tokens": total_tokens,
                "average_tokens_per_chunk": total_tokens // len(stored_chunks) if stored_chunks else 0,
                "chunk_ids": [c.id for c in stored_chunks]
            }
            
        except (ResourceNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Processing failed for asset {asset_id}: {str(e)}")
            raise DatabaseException(f"Asset processing failed: {str(e)}", operation="process")
    
    async def batch_process_assets(
        self,
        project_id: int,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        strategy: str = "size"
    ) -> Dict[str, Any]:
        """
        Process all unprocessed assets in a project
        
        Args:
            project_id: Project ID
            chunk_size: Size for chunking
            chunk_overlap: Overlap between chunks
            strategy: Chunking strategy
            
        Returns:
            Dictionary with batch processing results
            
        Raises:
            ResourceNotFoundException: If project not found
            DatabaseException: If processing fails
        """
        try:
            # Verify project exists
            project = await self.repo.get_project(project_id)
            if not project:
                raise ResourceNotFoundException("Project", project_id)
            
            # Get unprocessed assets
            assets_result = await self.db.execute(
                select(Asset).where(
                    Asset.project_id == project_id,
                    Asset.is_processed == False
                )
            )
            assets = assets_result.scalars().all()
            
            if not assets:
                self.logger.info(f"No unprocessed assets for project {project_id}")
                return {
                    "status": "success",
                    "project_id": project_id,
                    "total_assets": 0,
                    "processed_assets": 0,
                    "failed_assets": 0,
                    "results": []
                }
            
            self.logger.info(f"Processing {len(assets)} assets for project {project_id}")
            
            results = []
            failed = 0
            
            for asset in assets:
                try:
                    result = await self.process_asset(
                        project_id,
                        asset.id,
                        chunk_size,
                        chunk_overlap,
                        strategy
                    )
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Failed to process asset {asset.id}: {str(e)}")
                    failed += 1
            
            self.logger.info(
                f"Batch processing complete for project {project_id}: "
                f"{len(results)} successful, {failed} failed"
            )
            
            return {
                "status": "success",
                "project_id": project_id,
                "total_assets": len(assets),
                "processed_assets": len(results),
                "failed_assets": failed,
                "results": results
            }
            
        except ResourceNotFoundException:
            raise
        except Exception as e:
            self.logger.error(f"Batch processing failed for project {project_id}: {str(e)}")
            raise DatabaseException(
                f"Batch processing failed: {str(e)}",
                operation="batch_process"
            )
    
    def _chunk_text(
        self,
        text: str,
        strategy: str,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[str]:
        """
        Internal method to chunk text based on strategy
        
        Args:
            text: Text to chunk
            strategy: Chunking strategy
            chunk_size: Size parameter
            chunk_overlap: Overlap parameter
            
        Returns:
            List of text chunks
        """
        if strategy == "size":
            return ChunkingStrategy.chunk_by_size(text, chunk_size, chunk_overlap)
        elif strategy == "tokens":
            return ChunkingStrategy.chunk_by_tokens(text, chunk_size, chunk_overlap)
        elif strategy == "sentences":
            return ChunkingStrategy.chunk_by_sentences(text, chunk_size, chunk_overlap)
        elif strategy == "paragraphs":
            return ChunkingStrategy.chunk_by_paragraphs(text)
        else:
            self.logger.warning(f"Unknown strategy {strategy}, defaulting to 'size'")
            return ChunkingStrategy.chunk_by_size(text, chunk_size, chunk_overlap)
    
    async def get_chunk_stats(
        self,
        project_id: int,
        asset_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get statistics about chunks in a project or asset
        
        Args:
            project_id: Project ID
            asset_id: Optional asset ID to filter by
            
        Returns:
            Dictionary with chunk statistics
            
        Raises:
            ResourceNotFoundException: If project not found
        """
        try:
            # Verify project exists
            project = await self.repo.get_project(project_id)
            if not project:
                raise ResourceNotFoundException("Project", project_id)
            
            # Build query
            query = select(Chunk).where(Chunk.project_id == project_id)
            if asset_id:
                query = query.where(Chunk.asset_id == asset_id)
            
            result = await self.db.execute(query)
            chunks = result.scalars().all()
            
            if not chunks:
                return {
                    "project_id": project_id,
                    "asset_id": asset_id,
                    "total_chunks": 0,
                    "total_tokens": 0,
                    "avg_chunk_size": 0,
                    "min_chunk_size": 0,
                    "max_chunk_size": 0
                }
            
            token_counts = [c.token_count or 0 for c in chunks]
            chunk_sizes = [len(c.content) for c in chunks]
            
            return {
                "project_id": project_id,
                "asset_id": asset_id,
                "total_chunks": len(chunks),
                "total_tokens": sum(token_counts),
                "avg_chunk_size": sum(chunk_sizes) // len(chunk_sizes),
                "min_chunk_size": min(chunk_sizes),
                "max_chunk_size": max(chunk_sizes),
                "avg_tokens_per_chunk": sum(token_counts) // len(chunks),
                "min_tokens": min(token_counts),
                "max_tokens": max(token_counts)
            }
            
        except ResourceNotFoundException:
            raise
        except Exception as e:
            self.logger.error(f"Failed to get chunk stats: {str(e)}")
            raise DatabaseException(
                f"Failed to retrieve statistics: {str(e)}",
                operation="get_stats"
            )
