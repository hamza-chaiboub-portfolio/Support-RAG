
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
import sys

from controllers.UserController import UserController

async def test_auth_logic():
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_async_engine(DATABASE_URL)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        print("Testing authenticate_user for 'admin'...")
        try:
            user = await UserController.authenticate_user(
                db=session,
                username="admin",
                password="password123"
            )
            if user:
                print(f"AUTH SUCCESS: {user.username}")
            else:
                print("AUTH FAILED: Invalid credentials or user not found")
        except Exception as e:
            print(f"AUTH ERROR: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_auth_logic())
