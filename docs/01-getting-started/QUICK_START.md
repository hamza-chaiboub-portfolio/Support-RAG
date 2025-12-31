# Quick Start Guide

## 🚀 Run the Application

```bash
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Start the server
uvicorn src.main:app --reload --port 8000
```

Server will start at: http://127.0.0.1:8000

## 📚 Full Documentation

Read **`ARCHITECTURE.md`** for:
- Complete architecture explanation
- How all components work together
- What has been done and current status
- Database schema
- API endpoints
- Roadmap for next phases

## 🧪 Quick Test

```bash
# Health check (public)
curl http://localhost:8000/api/v1/health

# Login to get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# Use token on protected endpoint
curl http://localhost:8000/api/v1/metrics \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🎯 Current Status
✅ Application fully operational  
✅ Database connected  
✅ All 6 routes working  
✅ JWT authentication active  
✅ Ready for development  

## 📖 Documentation Structure
- **ARCHITECTURE.md** - Complete guide (everything you need to know)
- **README.md** - Project overview
- **docker/README.md** - Docker setup

All other documentation has been consolidated into ARCHITECTURE.md for clarity.