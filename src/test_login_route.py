
import asyncio
from fastapi import Request, Response
from pydantic import BaseModel
import os
import sys

from routes.auth import login, LoginRequest
from helpers.config import get_settings
from helpers.database import AsyncSessionLocal

async def test_login_route():
    settings = get_settings()
    # Mock Request and Response
    class MockRequest:
        def __init__(self):
            self.state = type('obj', (object,), {'csrf_token': 'test'})
            self.scope = {'type': 'http'}
            self.headers = {}
    
    class MockResponse:
        def set_cookie(self, *args, **kwargs):
            pass
            
    req = MockRequest()
    res = MockResponse()
    
    login_data = LoginRequest(username="admin", password="Password@123")
    
    print("Calling login route directly...")
    async with AsyncSessionLocal() as session:
        try:
            result = await login(
                request=req,
                response=res,
                login_data=login_data,
                db=session,
                settings=settings
            )
            print(f"RESULT: {result}")
        except Exception as e:
            print(f"ROUTE ERROR: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_login_route())
