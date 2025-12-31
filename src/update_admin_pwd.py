
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from models.user import User
from helpers.password import hash_password

async def update_password():
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_async_engine(DATABASE_URL)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        print("Updating admin password to 'Password@123'...")
        hashed = hash_password("Password@123")
        stmt = update(User).where(User.username == 'admin').values(hashed_password=hashed)
        await session.execute(stmt)
        await session.commit()
        print("Password updated successfully.")

if __name__ == "__main__":
    asyncio.run(update_password())
