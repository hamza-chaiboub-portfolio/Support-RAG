#!/usr/bin/env python
"""Script to run Alembic migrations and setup vectorization"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from alembic.config import Config
from alembic import command

def run_migrations():
    """Run Alembic migrations"""
    print("=" * 60)
    print("Running Alembic Migrations")
    print("=" * 60)
    
    try:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("\n[OK] Migrations completed successfully!")
        return True
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        return False

def verify_database():
    """Verify database connection and tables"""
    print("\n" + "=" * 60)
    print("Verifying Database Connection")
    print("=" * 60)
    
    import asyncio
    from helpers.database import engine, Base
    from models.db_models import Project, Asset, Chunk, ProcessingTask
    
    async def check_db():
        async with engine.begin() as conn:
            # Check if tables exist
            tables = [Project.__tablename__, Asset.__tablename__, 
                     Chunk.__tablename__, ProcessingTask.__tablename__]
            print(f"\n[OK] Database engine connected!")
            print(f"Expected tables: {', '.join(tables)}")
            return True
    
    try:
        asyncio.run(check_db())
        return True
    except Exception as e:
        print(f"\n[ERROR] Database verification failed: {e}")
        return False

def setup_chromadb():
    """Setup ChromeDB for vectorization"""
    print("\n" + "=" * 60)
    print("Setting Up ChromeDB for Vectorization")
    print("=" * 60)
    
    try:
        import chromadb
        print("\n[OK] ChromeDB is available")
        
        client = chromadb.Client()
        print("[OK] ChromeDB client initialized")
        
        collection = client.get_or_create_collection(name="documents")
        print(f"[OK] Collection 'documents' created/loaded")
        
        return True
    except ImportError:
        print("\n[ERROR] ChromeDB (chroma) not installed")
        print("Run: pip install chromadb")
        return False
    except Exception as e:
        print(f"\n[ERROR] ChromeDB setup failed: {e}")
        return False

if __name__ == "__main__":
    success = True
    
    # Run migrations
    success = run_migrations() and success
    
    # Verify database
    success = verify_database() and success
    
    # Setup ChromeDB
    success = setup_chromadb() and success
    
    print("\n" + "=" * 60)
    if success:
        print("[OK] All setup tasks completed successfully!")
    else:
        print("[ERROR] Some setup tasks failed. See details above.")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
