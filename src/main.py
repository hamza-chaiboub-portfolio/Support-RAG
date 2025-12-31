from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware import Middleware
from contextlib import asynccontextmanager
import sys
import os
from pathlib import Path
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

sys.path.insert(0, str(Path(__file__).parent))

try:
    from helpers.config import get_settings
except ImportError:
    from src.helpers.config import get_settings

try:
    from helpers.secrets import SecretsManager
except ImportError:
    from src.helpers.secrets import SecretsManager

settings = get_settings()

try:
    from routes import base, auth, nlp, processing, rag, gdpr, api_keys
except ImportError:
    from src.routes import base, auth, nlp, processing, rag, gdpr, api_keys

try:
    from helpers.database import init_db, close_db
except ImportError:
    from src.helpers.database import init_db, close_db

try:
    from helpers.limiter import limiter
except ImportError:
    from src.helpers.limiter import limiter

try:
    from middleware.audit import AuditMiddleware
except ImportError:
    from src.middleware.audit import AuditMiddleware

try:
    from middleware.csrf import CSRFMiddleware
except ImportError:
    from src.middleware.csrf import CSRFMiddleware

try:
    from middleware.security_headers import SecurityHeadersMiddleware
except ImportError:
    from src.middleware.security_headers import SecurityHeadersMiddleware

try:
    from routes import data
    DATA_ROUTER_AVAILABLE = True
except (ImportError, AttributeError):
    try:
        from src.routes import data
        DATA_ROUTER_AVAILABLE = True
    except (ImportError, AttributeError):
        DATA_ROUTER_AVAILABLE = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - startup and shutdown"""
    print("[STARTUP] Starting up application...")
    
    try:
        SecretsManager.validate_secrets()
        print("[SUCCESS] Secrets validation passed")
    except Exception as e:
        print(f"[ERROR] Secrets validation failed: {e}")
        raise
    
    try:
        await init_db()
        print("[SUCCESS] Database initialized successfully")
    except Exception as e:
        print(f"[WARNING] Database initialization warning: {e}")
    
    yield
    
    print("[SHUTDOWN] Shutting down application...")
    try:
        await close_db()
        print("[SUCCESS] Database connection closed")
    except Exception as e:
        print(f"[WARNING] Error closing database: {e}")


app = FastAPI(
    title="SupportRAG AI",
    description="FastAPI-based RAG Application with JWT Authentication and Security",
    version="2.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(SlowAPIMiddleware)

if os.getenv("TESTING") != "true":
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=settings.ALLOWED_HOSTS
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-CSRF-Token"],
    max_age=3600,
)

app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(CSRFMiddleware)

app.add_middleware(AuditMiddleware)

# Add Prometheus Middleware
try:
    from starlette_exporter import PrometheusMiddleware, handle_metrics
    app.add_middleware(PrometheusMiddleware, app_name="supportrag-ai", group_paths=True)
    app.add_route("/metrics", handle_metrics)
except ImportError:
    print("[WARNING] starlette_exporter not installed, skipping Prometheus middleware")

app.include_router(base.base_router)
app.include_router(auth.auth_router)
app.include_router(gdpr.gdpr_router)
app.include_router(nlp.nlp_router)
app.include_router(processing.processing_router)
app.include_router(rag.rag_router)
app.include_router(api_keys.api_key_router)

if DATA_ROUTER_AVAILABLE:
    app.include_router(data.data_router)