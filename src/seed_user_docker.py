
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

from controllers.UserController import UserController
from models.user import UserRole

async def seed_user():
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_async_engine(DATABASE_URL)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        print("Creating admin user inside container...")
        user = await UserController.create_user(
            db=session,
            username="admin",
            email="admin@example.com",
            password="password123",
            role=UserRole.ADMIN
        )
        print(f"User created: {user.username}")

if __name__ == "__main__":
    asyncio.run(seed_user())
