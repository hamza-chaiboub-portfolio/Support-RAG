
import asyncio
import os
from helpers.jwt_handler import create_access_token
from helpers.config import get_settings

async def test_jwt():
    settings = get_settings()
    data = {"sub": "admin", "user_id": 1, "role": "admin"}
    print(f"Creating token for: {data}")
    try:
        token = create_access_token(data=data, settings=settings)
        print(f"Token created: {token[:20]}...")
    except Exception as e:
        print(f"JWT ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_jwt())
