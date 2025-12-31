
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from models.db_models import Project

async def seed_data():
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@postgres:5432/supportrag")
    engine = create_async_engine(DATABASE_URL)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        # Check if project 1 exists
        result = await session.execute(select(Project).where(Project.id == 1))
        project = result.scalar_one_or_none()
        
        if not project:
            print("Creating Project 1...")
            new_project = Project(
                id=1,
                name="Default Project",
                description="Default project for SupportRAG"
            )
            session.add(new_project)
            await session.commit()
            print("Project 1 created.")
        else:
            print("Project 1 already exists.")

if __name__ == "__main__":
    asyncio.run(seed_data())
