"""Integration tests for RAG pipeline"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from controllers.NLPController import NLPController
from controllers.ProcessingController import ProcessingController
from controllers.RAGController import RAGController
from models.db_models import Project, Asset, Chunk, ProjectStatus, AssetType
from helpers.exceptions import ResourceNotFoundException, ValidationException, DatabaseException


@pytest.fixture
async def mock_project():
    """Create mock project"""
    project = MagicMock(spec=Project)
    project.id = 1
    project.name = "Test Project"
    project.status = ProjectStatus.ACTIVE
    return project


@pytest.fixture
async def mock_asset():
    """Create mock asset"""
    asset = MagicMock(spec=Asset)
    asset.id = 1
    asset.project_id = 1
    asset.filename = "test.pdf"
    asset.asset_type = AssetType.PDF
    asset.file_path = "/tmp/test.pdf"
    asset.is_processed = False
    return asset


@pytest.fixture
async def mock_chunks():
    """Create mock chunks"""
    chunks = []
    for i in range(3):
        chunk = MagicMock(spec=Chunk)
        chunk.id = i + 1
        chunk.project_id = 1
        chunk.asset_id = 1
        chunk.content = f"Test chunk content {i+1}"
        chunk.chunk_index = i
        chunk.token_count = 100
        chunk.embedding_vector = None
        chunks.append(chunk)
    return chunks


@pytest.mark.asyncio
async def test_nlp_vectorize_chunks_success(mock_project):
    """Test successful chunk vectorization"""
    db = AsyncMock(spec=AsyncSession)
    
    mock_chunks = [
        MagicMock(id=1, content="Text 1", project_id=1, asset_id=1, chunk_index=0, token_count=100),
        MagicMock(id=2, content="Text 2", project_id=1, asset_id=1, chunk_index=1, token_count=100),
    ]
    
    # Mock repository
    with patch('controllers.NLPController.ProjectRepository') as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo.get_project = AsyncMock(return_value=mock_project)
        mock_repo_class.return_value = mock_repo
        
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_chunks
        db.execute = AsyncMock(return_value=mock_result)
        
        # Mock vector store
        with patch('controllers.NLPController.VectorStore') as mock_store_class:
            mock_store = MagicMock()
            mock_store.add_documents = MagicMock()
            mock_store.persist = MagicMock()
            mock_store_class.return_value = mock_store
            
            # Mock embedding service
            with patch('controllers.NLPController.AsyncEmbeddingService') as mock_embed_class:
                mock_embed = MagicMock()
                mock_embed.embed_documents_async = AsyncMock(
                    return_value=[[0.1, 0.2], [0.3, 0.4]]
                )
                mock_embed_class.return_value = mock_embed
                
                controller = NLPController(db)
                result = await controller.vectorize_chunks(
                    project_id=1,
                    batch_size=32
                )
                
                assert result["status"] == "success"
                assert result["project_id"] == 1
                assert result["chunks_vectorized"] == 2


@pytest.mark.asyncio
async def test_nlp_search_similar_chunks_success(mock_project):
    """Test successful semantic search"""
    db = AsyncMock(spec=AsyncSession)
    
    # Mock repository
    with patch('controllers.NLPController.ProjectRepository') as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo.get_project = AsyncMock(return_value=mock_project)
        mock_repo_class.return_value = mock_repo
        
        # Mock vector store
        with patch('controllers.NLPController.VectorStore') as mock_store_class:
            mock_store = MagicMock()
            mock_store.query = MagicMock(return_value={
                "ids": [["chunk_1", "chunk_2"]],
                "documents": [["Doc 1", "Doc 2"]],
                "metadatas": [[
                    {"chunk_id": 1, "project_id": 1, "asset_id": 1},
                    {"chunk_id": 2, "project_id": 1, "asset_id": 1}
                ]],
                "distances": [[0.1, 0.2]]
            })
            mock_store_class.return_value = mock_store
            
            # Mock embedding service
            with patch('controllers.NLPController.AsyncEmbeddingService') as mock_embed_class:
                mock_embed = MagicMock()
                mock_embed.embed_query_async = AsyncMock(return_value=[0.1, 0.2])
                mock_embed_class.return_value = mock_embed
                
                controller = NLPController(db)
                results = await controller.search_similar_chunks(
                    project_id=1,
                    query="test query",
                    n_results=5
                )
                
                assert len(results) == 2
                assert results[0]["similarity_score"] == 0.9


@pytest.mark.asyncio
async def test_processing_asset_success(mock_project, mock_asset):
    """Test successful asset processing"""
    db = AsyncMock(spec=AsyncSession)
    
    # Mock repository
    with patch('controllers.ProcessingController.ProjectRepository') as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo.get_project = AsyncMock(return_value=mock_project)
        mock_repo_class.return_value = mock_repo
        
        # Mock database query and commit
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_asset
        db.execute = AsyncMock(return_value=mock_result)
        db.add = MagicMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        
        # Mock document processor
        with patch('controllers.ProcessingController.DocumentProcessor') as mock_proc_class:
            mock_proc = MagicMock()
            mock_proc.extract_text = MagicMock(return_value="Test text content for chunking")
            mock_proc_class.return_value = mock_proc
            
            # Mock chunking strategy
            with patch('controllers.ProcessingController.ChunkingStrategy') as mock_chunk_class:
                mock_chunk_class.chunk_by_size.return_value = ["Chunk 1", "Chunk 2", "Chunk 3"]
                
                # Mock token counter and file existence check
                with patch('controllers.ProcessingController.TokenCounter.count_tokens', return_value=100):
                    with patch('os.path.exists', return_value=True):
                        controller = ProcessingController(db)
                        result = await controller.process_asset(
                            project_id=1,
                            asset_id=1,
                            chunk_size=512
                        )
                        
                        assert result["status"] == "success"
                        assert result["chunks_created"] == 3
                        assert result["asset_id"] == 1


@pytest.mark.asyncio
async def test_rag_query_success(mock_project):
    """Test successful RAG query"""
    db = AsyncMock(spec=AsyncSession)
    
    # Mock LLM provider
    mock_llm = MagicMock()
    mock_llm.generate_with_context = AsyncMock(
        return_value="Generated response based on context"
    )
    
    # Mock repository
    with patch('controllers.RAGController.ProjectRepository') as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo.get_project = AsyncMock(return_value=mock_project)
        mock_repo_class.return_value = mock_repo
        
        # Mock NLP controller
        with patch('controllers.RAGController.NLPController') as mock_nlp_class:
            mock_nlp = MagicMock()
            mock_nlp.search_similar_chunks = AsyncMock(return_value=[
                {
                    "chunk_id": 1,
                    "asset_id": 1,
                    "project_id": 1,
                    "content": "Retrieved context",
                    "similarity_score": 0.9,
                    "metadata": {}
                }
            ])
            mock_nlp_class.return_value = mock_nlp
            
            controller = RAGController(db, llm_provider=mock_llm)
            result = await controller.rag_query(
                project_id=1,
                query="test query"
            )
            
            assert result["status"] == "success"
            assert result["retrieved_count"] == 1
            assert result["response"] == "Generated response based on context"
            assert result["generation_status"] == "success"


@pytest.mark.asyncio
async def test_rag_query_no_results(mock_project):
    """Test RAG query with no retrieval results"""
    db = AsyncMock(spec=AsyncSession)
    
    # Mock repository
    with patch('controllers.RAGController.ProjectRepository') as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo.get_project = AsyncMock(return_value=mock_project)
        mock_repo_class.return_value = mock_repo
        
        # Mock NLP controller with empty results
        with patch('controllers.RAGController.NLPController') as mock_nlp_class:
            mock_nlp = MagicMock()
            mock_nlp.search_similar_chunks = AsyncMock(return_value=[])
            mock_nlp_class.return_value = mock_nlp
            
            controller = RAGController(db)
            result = await controller.rag_query(
                project_id=1,
                query="test query"
            )
            
            assert result["status"] == "success"
            assert result["retrieved_count"] == 0
            assert result["generation_status"] == "no_context"


@pytest.mark.asyncio
async def test_save_embeddings_success(mock_project, mock_chunks):
    """Test successful embedding persistence"""
    db = AsyncMock(spec=AsyncSession)
    
    # Mock repository
    with patch('controllers.RAGController.ProjectRepository') as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo.get_project = AsyncMock(return_value=mock_project)
        mock_repo_class.return_value = mock_repo
        
        # Mock database query and commit
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_chunks
        db.execute = AsyncMock(return_value=mock_result)
        db.add = MagicMock()
        db.commit = AsyncMock()
        
        # Mock NLP controller
        with patch('controllers.RAGController.NLPController') as mock_nlp_class:
            mock_nlp = MagicMock()
            mock_nlp.embedding_service = MagicMock()
            mock_nlp.embedding_service.embed_documents_async = AsyncMock(
                return_value=[[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
            )
            mock_nlp_class.return_value = mock_nlp
            
            controller = RAGController(db)
            result = await controller.save_embeddings_to_db(project_id=1)
            
            assert result["status"] == "success"
            assert result["chunks_updated"] == 3
            assert result["embedding_dimension"] == 2


@pytest.mark.asyncio
async def test_nlp_vectorize_project_not_found(mock_project):
    """Test vectorization with nonexistent project"""
    db = AsyncMock(spec=AsyncSession)
    
    with patch('controllers.NLPController.ProjectRepository') as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo.get_project = AsyncMock(return_value=None)
        mock_repo_class.return_value = mock_repo
        
        controller = NLPController(db)
        with pytest.raises(ResourceNotFoundException):
            await controller.vectorize_chunks(project_id=999)


@pytest.mark.asyncio
async def test_search_empty_query(mock_project):
    """Test search with empty query"""
    db = AsyncMock(spec=AsyncSession)
    
    with patch('controllers.NLPController.ProjectRepository') as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo.get_project = AsyncMock(return_value=mock_project)
        mock_repo_class.return_value = mock_repo
        
        controller = NLPController(db)
        with pytest.raises(ValidationException):
            await controller.search_similar_chunks(
                project_id=1,
                query=""
            )


@pytest.mark.asyncio
async def test_rerank_results_success(mock_project):
    """Test result re-ranking"""
    db = AsyncMock(spec=AsyncSession)
    
    with patch('controllers.NLPController.ProjectRepository') as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        
        with patch('controllers.NLPController.AsyncEmbeddingService') as mock_embed_class:
            mock_embed = MagicMock()
            mock_embed.embed_query_async = AsyncMock(return_value=[0.1, 0.2])
            mock_embed.embed_documents_async = AsyncMock(
                return_value=[[0.15, 0.25], [0.05, 0.15], [0.12, 0.22]]
            )
            mock_embed_class.return_value = mock_embed
            
            controller = NLPController(db)
            ranked = await controller.rerank_results(
                query="test query",
                documents=["Doc 1", "Doc 2", "Doc 3"],
                method="similarity"
            )
            
            assert len(ranked) == 3
            # Results should be sorted by score (descending)
            for i in range(len(ranked) - 1):
                assert ranked[i][1] >= ranked[i+1][1]
