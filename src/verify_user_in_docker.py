
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import os

# Assuming this script is run inside the container where src is in PYTHONPATH
from models.user import User

async def check_users():
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_async_engine(DATABASE_URL)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.username == 'admin'))
        user = result.scalar_one_or_none()
        
        if not user:
            print("USER_NOT_FOUND")
        else:
            print(f"USER_FOUND: {user.username}, Active: {user.is_active}")

if __name__ == "__main__":
    asyncio.run(check_users())
