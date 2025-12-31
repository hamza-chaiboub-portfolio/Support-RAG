import time
import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from helpers.logger import logger

try:
    import jwt
    from helpers.config import get_settings
except ImportError:
    jwt = None
    get_settings = None


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive audit logging middleware.
    Logs all requests with user identification when available.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Skip audit logging for metrics endpoint
        if request.url.path == "/metrics":
            return await call_next(request)
            
        start_time = time.time()
        
        user_id = "anonymous"
        user_role = None
        
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            if jwt and get_settings:
                try:
                    token = auth_header[7:]
                    settings = get_settings()
                    decoded = jwt.decode(
                        token,
                        settings.JWT_SECRET_KEY,
                        algorithms=[settings.JWT_ALGORITHM]
                    )
                    user_id = decoded.get("sub", "unknown")
                    user_role = decoded.get("role", None)
                except Exception:
                    user_id = "invalid_token"
        
        response = await call_next(request)
        process_time = time.time() - start_time
        
        log_entry = {
            "type": "audit",
            "timestamp": time.time(),
            "method": request.method,
            "path": request.url.path,
            "query_string": str(request.url.query) if request.url.query else None,
            "status_code": response.status_code,
            "user_id": user_id,
            "user_role": user_role,
            "ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "duration_ms": round(process_time * 1000, 2)
        }
        
        logger.info(json.dumps(log_entry))
        
        return response
