# SupportRAG AI - Quick Start Guide

Get up and running with SupportRAG AI in 5 minutes!

---

## Prerequisites

- Python 3.9+
- Node.js 16+
- Docker & Docker Compose (optional but recommended)

---

## Option 1: Docker Setup (Fastest)

### 1. Start All Services

```bash
cd docker
docker-compose up -d
```

### 2. Wait for Services to Be Ready

```bash
# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Access Applications

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)

### 4. Login to Application

1. Go to http://localhost:3000
2. Default credentials:
   - Email: `admin@example.com`
   - Password: `password123`

---

## Option 2: Local Development Setup

### Backend Setup

```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\Activate.ps1

# 2. Install dependencies
cd src
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env

# 4. Initialize database
python ../run_migrations.py

# 5. Start backend
uvicorn main:app --reload
```

**Backend ready at**: http://localhost:8000

### Frontend Setup

```bash
# 1. Install dependencies
cd frontend
npm install

# 2. Configure environment
cp .env.example .env

# 3. Start development server
npm run dev
```

**Frontend ready at**: http://localhost:5173

---

## First Steps

### 1. Test Health Check

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### 2. Login and Get Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin@example.com",
    "password": "password123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Use Token for Protected Endpoints

```bash
curl -X POST http://localhost:8000/api/v1/rag/query \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is RAG?"
  }'
```

---

## Try the UI

### Chat Interface

1. Open http://localhost:3000 (or 3000)
2. You're already logged in
3. Type a message in the chat box
4. Press Enter or click Send
5. Wait for the response

### Features to Try

- **Chat**: Send messages and get AI responses
- **Citations**: See source references in responses
- **File Upload**: Upload documents for processing
- **GDPR**: Export your data or request deletion
- **Logout**: End your session

---

## Key Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login

### RAG Pipeline
- `POST /api/v1/rag/query` - Query with RAG
- `POST /api/v1/rag/retrieve` - Retrieve documents
- `POST /api/v1/rag/embed` - Generate embeddings

### File Processing
- `POST /api/v1/processing/upload` - Upload document

### GDPR
- `POST /api/v1/gdpr/export` - Request data export
- `POST /api/v1/gdpr/delete` - Request data deletion

### Health
- `GET /api/v1/health` - Health check
- `GET /api/v1/` - Application info

Full API docs: http://localhost:8000/api/docs

---

## Running Tests

### Backend Tests

```bash
cd src
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

### All Tests

```bash
# Backend
cd src && pytest

# Frontend
cd frontend && npm test
```

Expected: **255+ tests passing** ✅

---

## Common Commands

```bash
# Backend
cd src
uvicorn main:app --reload      # Start dev server
pytest                          # Run tests
pytest --cov=src               # Test with coverage
python -m black .              # Format code

# Frontend
cd frontend
npm run dev                     # Start dev server
npm test                        # Run tests
npm run build                   # Build for production
npm run lint                    # Check code quality

# Docker
cd docker
docker-compose up -d            # Start all services
docker-compose down             # Stop services
docker-compose logs -f          # View logs
docker-compose ps               # Check status
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find process on port 8000
lsof -i :8000
kill -9 <PID>

# Or use different port
uvicorn main:app --port 8001
```

### Database Connection Error

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Restart it
docker-compose restart postgres
```

### CORS Error

Make sure frontend and backend URLs are configured:

**Frontend (.env)**:
```
VITE_API_URL=http://localhost:8000
```

**Backend (.env)**:
```
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

### Token Expired

Just login again:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@example.com","password":"password123"}'
```

---

## Next Steps

1. **Read the Full Documentation**: `COMPLETE_DOCUMENTATION.md`
2. **Explore the API**: Visit http://localhost:8000/api/docs
3. **Check Code Quality**: Review test results
4. **Deploy to Production**: See deployment guide
5. **Configure for Your Use Case**: Customize models and settings

---

## Support

- 📚 **Documentation**: See `docs/` directory
- 🧪 **Tests**: Run `pytest` or `npm test`
- 🐛 **Issues**: Check GitHub Issues
- 💬 **Discussions**: GitHub Discussions

---

**Enjoy using SupportRAG AI!** 🚀
