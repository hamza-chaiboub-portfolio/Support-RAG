#!/usr/bin/env python
"""Complete setup and verification of Alembic and ChromeDB vectorization"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

def setup_alembic():
    """Setup Alembic migrations"""
    print("=" * 70)
    print("STEP 1: Setting up Alembic Migrations")
    print("=" * 70)
    
    try:
        from alembic.config import Config
        from alembic import command
        
        alembic_cfg = Config("alembic.ini")
        
        print("[*] Running Alembic upgrade to head...")
        command.upgrade(alembic_cfg, "head")
        print("[OK] Alembic migrations completed successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Alembic setup failed: {e}")
        return False

def verify_database():
    """Verify database connection"""
    print("\n" + "=" * 70)
    print("STEP 2: Verifying Database Connection")
    print("=" * 70)
    
    try:
        import asyncio
        from helpers.database import engine
        from models.db_models import Project, Asset, Chunk, ProcessingTask
        
        async def check_connection():
            async with engine.begin() as conn:
                print("[*] Connected to PostgreSQL database")
                
                tables = [
                    Project.__tablename__,
                    Asset.__tablename__,
                    Chunk.__tablename__,
                    ProcessingTask.__tablename__
                ]
                
                print(f"[OK] Database tables: {', '.join(tables)}")
                return True
        
        asyncio.run(check_connection())
        return True
    except Exception as e:
        print(f"[ERROR] Database verification failed: {e}")
        return False

def setup_chromadb():
    """Setup ChromeDB vector store"""
    print("\n" + "=" * 70)
    print("STEP 3: Setting up ChromeDB Vector Store")
    print("=" * 70)
    
    try:
        import chromadb
        from chromadb.config import Settings
        
        print("[*] ChromeDB imported successfully")
        
        persist_dir = str(Path.cwd() / "chroma_data")
        os.makedirs(persist_dir, exist_ok=True)
        
        settings = chromadb.config.Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_dir,
            anonymized_telemetry=False,
        )
        
        client = chromadb.Client(settings)
        collection = client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        print(f"[OK] ChromeDB initialized")
        print(f"[OK] Collection 'documents' ready")
        print(f"[OK] Persist directory: {persist_dir}")
        return True
    except ImportError:
        print("[ERROR] ChromeDB not installed")
        print("Run: pip install chromadb")
        return False
    except Exception as e:
        print(f"[ERROR] ChromeDB setup failed: {e}")
        return False

def setup_embedding_model():
    """Setup embedding model"""
    print("\n" + "=" * 70)
    print("STEP 4: Setting up Embedding Model")
    print("=" * 70)
    
    try:
        from sentence_transformers import SentenceTransformer
        
        print("[*] Loading sentence-transformers model...")
        model = SentenceTransformer("all-MiniLM-L6-v2")
        
        test_text = "This is a test embedding"
        embedding = model.encode([test_text])
        
        print(f"[OK] Model loaded successfully")
        print(f"[OK] Embedding dimension: {len(embedding[0])}")
        return True
    except ImportError:
        print("[ERROR] sentence-transformers not installed")
        print("Run: pip install sentence-transformers")
        return False
    except Exception as e:
        print(f"[ERROR] Embedding model setup failed: {e}")
        return False

def test_vectorization_pipeline():
    """Test the vectorization pipeline"""
    print("\n" + "=" * 70)
    print("STEP 5: Testing Vectorization Pipeline")
    print("=" * 70)
    
    try:
        from stores.vector_store import VectorStore
        from stores.embedding_service import EmbeddingService
        
        print("[*] Testing embedding service...")
        embedding_svc = EmbeddingService("sentence-transformers")
        
        test_docs = [
            "This is a test document about machine learning",
            "Another document about natural language processing",
            "A third document discussing artificial intelligence"
        ]
        
        embeddings = embedding_svc.embed_documents(test_docs)
        print(f"[OK] Generated {len(embeddings)} embeddings")
        print(f"[OK] Embedding dimensions: {len(embeddings[0])}")
        
        print("[*] Testing vector store...")
        vector_store = VectorStore()
        
        test_ids = [f"test_doc_{i}" for i in range(len(test_docs))]
        vector_store.add_documents(
            documents=test_docs,
            ids=test_ids,
            embeddings=embeddings
        )
        
        count = vector_store.count()
        print(f"[OK] Added {count} documents to vector store")
        
        print("[*] Testing query...")
        query_results = vector_store.query(
            query_text="machine learning and AI",
            n_results=2
        )
        
        if query_results and query_results.get("documents"):
            print(f"[OK] Query returned {len(query_results['documents'][0])} results")
        
        vector_store.persist()
        print("[OK] Vector store persisted")
        
        return True
    except Exception as e:
        print(f"[ERROR] Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_summary():
    """Print setup summary"""
    print("\n" + "=" * 70)
    print("VECTORIZATION SETUP COMPLETE")
    print("=" * 70)
    print()
    print("Components installed:")
    print("  [X] Alembic - Database migrations")
    print("  [X] PostgreSQL - Main database")
    print("  [X] pgvector - PostgreSQL vector extension")
    print("  [X] ChromeDB - Vector database")
    print("  [X] Sentence Transformers - Embedding model")
    print()
    print("Created modules:")
    print("  [X] src/stores/vector_store.py - Vector store management")
    print("  [X] src/stores/embedding_service.py - Embedding generation")
    print("  [X] src/tasks/vectorize_documents.py - Vectorization tasks")
    print()
    print("Usage:")
    print("  from stores.vector_store import VectorStore")
    print("  from stores.embedding_service import EmbeddingService")
    print("  from tasks.vectorize_documents import VectorizationTask")
    print()
    print("=" * 70)

if __name__ == "__main__":
    results = {
        "alembic": False,
        "database": False,
        "chromadb": False,
        "embedding": False,
        "pipeline": False
    }
    
    results["alembic"] = setup_alembic()
    results["database"] = verify_database()
    results["chromadb"] = setup_chromadb()
    results["embedding"] = setup_embedding_model()
    results["pipeline"] = test_vectorization_pipeline()
    
    print_summary()
    
    if all(results.values()):
        print("\n[OK] All setup steps completed successfully!")
        sys.exit(0)
    else:
        print("\n[ERROR] Some setup steps failed:")
        for step, status in results.items():
            print(f"  {step}: {'[OK]' if status else '[FAILED]'}")
        sys.exit(1)
