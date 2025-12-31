# SupportRAG AI

> An enterprise-grade **RAG (Retrieval-Augmented Generation)** platform with intelligent document processing, semantic search, and background task automation.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-15-336791.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/docker-compose-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 🎯 Overview

SupportRAG AI is a full-stack intelligent document processing system that combines modern LLM capabilities with RAG pipelines. It enables organizations to:

- **Upload & Extract** documents (PDF, DOCX, TXT)
- **Vectorize & Index** content with semantic embeddings
- **Search Intelligently** with semantic and hybrid search
- **Generate Answers** using LLM-powered RAG
- **Process Asynchronously** with background task workers
- **Monitor Operations** with real-time dashboards

### 🎁 Key Features

- ✅ **FastAPI Backend** - High-performance async API with automatic documentation
- ✅ **JWT Authentication** - Secure token-based authentication with role management
- ✅ **Document Processing** - Extract text from PDF, DOCX, TXT with chunking
- ✅ **Vector Search** - Semantic search with embeddings (sentence-transformers)
- ✅ **RAG Pipeline** - Retrieval-augmented generation for context-aware responses
- ✅ **Celery Workers** - Async background processing with Redis
- ✅ **PostgreSQL** - ACID-compliant database with vector storage
- ✅ **Docker Compose** - Production-ready containerized environment
- ✅ **Monitoring** - Prometheus metrics, Grafana dashboards, Flower task monitoring
- ✅ **GDPR Compliant** - Built-in data deletion and privacy controls
- ✅ **Comprehensive Tests** - Unit, integration, and E2E test coverage

---

## 🚀 Quick Start

### Prerequisites
- **Docker & Docker Compose** (recommended)
- **Python 3.11+** (for local development)
- **PostgreSQL 15** (or use Docker)
- **Redis 7+** (for Celery, or use Docker)

### Option 1: Docker Compose (Recommended)

```bash
# Clone repository
git clone <repo-url>
cd SupportRAG_AI

# Start all services
docker-compose -f docker/docker-compose.yml up -d

# Initialize database
docker-compose -f docker/docker-compose.yml exec app python -m alembic upgrade head

# Access services
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Frontend: http://localhost:3000
# - Flower (Tasks): http://localhost:5555
# - Grafana (Metrics): http://localhost:3001
```

### Option 2: Local Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r src/requirements.txt

# Setup environment
cp src/.env.example .env
# Edit .env with your configuration

# Start PostgreSQL and Redis
docker run -d --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:15-alpine
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Run migrations
python run_migrations.py

# Start backend server
uvicorn src.main:app --reload

# Start Celery worker (another terminal)
celery -A src.celery_app worker --loglevel=info

# Start Flower monitoring (optional)
celery -A src.celery_app flower --port=5555
```

---

## 📚 Documentation

Complete documentation is organized in the `docs/` directory:

### Getting Started
- [Quick Start Guide](./docs/01-getting-started/QUICK_START.md) - 5-minute setup
- [Project Overview](./docs/01-getting-started/README.md) - Features

### Architecture & Development
- [Complete Architecture](./docs/02-architecture/ARCHITECTURE.md) - System design
- [Architecture Manifest](./docs/02-architecture/ARCHITECTURE_UPDATE_MANIFEST.md) - Implementation details

### Deployment
- [Docker Guide](./docs/04-deployment/DOCKER.md) - Deployment instructions
- [API Reference](./API_REFERENCE.md) - All endpoints

### Full Reference
- [Complete Technical Documentation](./COMPLETE_DOCUMENTATION.md) - 20,000+ word guide
- [Documentation Hub](./docs/INDEX.md) - Navigation center

---

## 🏗️ Project Structure

```
SupportRAG_AI/
├── src/                    # Backend application
│   ├── main.py            # FastAPI entry point
│   ├── celery_app.py      # Celery configuration
│   ├── controllers/       # Business logic layer
│   ├── routes/            # API endpoints
│   ├── models/            # Data models & ORM
│   ├── repositories/      # Data access layer
│   ├── schemas/           # Pydantic schemas
│   ├── helpers/           # Utilities & config
│   ├── middleware/        # Middleware
│   ├── tasks/             # Celery tasks
│   └── stores/            # Service integration
│
├── frontend/              # React/Vite frontend
├── docker/                # Docker configuration
├── docs/                  # Complete documentation
├── tests/                 # Test suite
├── alembic/               # Database migrations
├── README.md             # This file
├── LICENSE
└── .env                   # Configuration
```

---

## 🔧 Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Web Framework** | FastAPI | 0.104.1+ |
| **ASGI Server** | Uvicorn | 0.24.0+ |
| **Database** | PostgreSQL | 15 |
| **ORM** | SQLAlchemy | 2.0+ |
| **Async Tasks** | Celery | 5.3.0+ |
| **Message Broker** | Redis | 7.0+ |
| **Authentication** | JWT | 2.8.0+ |
| **Embeddings** | sentence-transformers | 2.2.2+ |
| **Frontend** | React 18+ | - |
| **Styling** | Tailwind CSS | - |

---

## 📖 Key Concepts

### RAG Pipeline
1. **Document Ingestion** - Extract text from uploads
2. **Chunking** - Split into semantic chunks
3. **Embedding** - Convert to vector embeddings
4. **Indexing** - Store in vector database
5. **Retrieval** - Find relevant chunks
6. **Generation** - LLM response generation

### Vector Storage
- **Primary**: PostgreSQL with jsonb/text-based vectors
- **Alternative**: ChromeDB for local development

### Background Tasks
Celery workers handle:
- Document vectorization
- Large file processing
- Report generation
- Batch operations

---

## 🔐 Security

- ✅ JWT Authentication with expiration
- ✅ Password Hashing (bcrypt)
- ✅ CORS Configuration with whitelisting
- ✅ SQL Injection Prevention
- ✅ CSRF Protection
- ✅ Rate Limiting
- ✅ Secrets Management
- ✅ GDPR Compliance
- ✅ Encryption at rest

---

## 📊 Monitoring & Operations

### Prometheus Metrics
- HTTP request metrics
- Database stats
- Celery task metrics
- Custom application metrics

### Grafana Dashboards
- System health and performance
- Request rates and latencies
- Database metrics
- Worker status

### Flower Web UI
Access at `http://localhost:5555`
- Task monitoring
- Worker status
- Execution history

---

## 🧪 Testing

```bash
# Install test dependencies
pip install -r src/requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific suites
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

Target Coverage: **80%+**

---

## 🚀 Deployment

### Docker Compose

```bash
docker-compose -f docker/docker-compose.yml up -d
```

Services:
- Backend API (port 8000)
- Frontend (port 3000)
- PostgreSQL (port 5432)
- Redis (port 6379)
- Celery Worker
- Flower (port 5555)
- Prometheus (port 9090)
- Grafana (port 3001)

See [Deployment Guide](./docs/04-deployment/DOCKER.md) for production setup.

---

## 🔄 Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 📝 API Endpoints

Quick reference (full docs at `/docs`):

```
Authentication
  POST   /api/v1/auth/register
  POST   /api/v1/auth/login
  POST   /api/v1/auth/refresh
  POST   /api/v1/auth/logout

Projects
  GET    /api/v1/projects
  POST   /api/v1/projects
  GET    /api/v1/projects/{id}
  PUT    /api/v1/projects/{id}
  DELETE /api/v1/projects/{id}

Documents
  POST   /api/v1/projects/{id}/documents
  GET    /api/v1/projects/{id}/documents
  DELETE /api/v1/documents/{id}

RAG Pipeline
  POST   /api/v1/projects/{id}/search
  POST   /api/v1/projects/{id}/generate
  POST   /api/v1/projects/{id}/vectorize

Admin
  GET    /api/v1/health
  GET    /api/v1/metrics
  DELETE /api/v1/admin/data/{id}
```

Full documentation: [API_REFERENCE.md](./API_REFERENCE.md)

---

## 🐛 Troubleshooting

**Database Connection Error**
```bash
docker-compose -f docker/docker-compose.yml ps postgres
# Check DATABASE_URL in .env
```

**Celery Worker Not Processing**
```bash
docker-compose -f docker/docker-compose.yml ps redis
# Verify CELERY_BROKER_URL in .env
```

**Document Upload Fails**
```bash
pip install python-docx pypdf
# Check disk space and file permissions
```

See [COMPLETE_DOCUMENTATION.md](./COMPLETE_DOCUMENTATION.md) for comprehensive troubleshooting.

---

## 📞 Support & Resources

- **Documentation Hub**: [docs/INDEX.md](./docs/INDEX.md)
- **API Docs**: http://localhost:8000/docs (interactive)
- **Architecture**: [ARCHITECTURE.md](./docs/02-architecture/ARCHITECTURE.md)
- **Quick Start**: [QUICK_START_GUIDE.md](./QUICK_START_GUIDE.md)
- **Technical Ref**: [COMPLETE_DOCUMENTATION.md](./COMPLETE_DOCUMENTATION.md)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

## 🎉 Acknowledgments

Built with:
- **FastAPI** - Modern async web framework
- **SQLAlchemy** - Robust ORM
- **Celery** - Reliable task queue
- **Hugging Face** - sentence-transformers
- **OpenRouter** - LLM API aggregation

---

## 📈 Project Status

**Version**: 1.0  
**Phase**: Phase 4 Complete  
**Updated**: December 2024

### Completed ✅
- Core backend infrastructure
- Document processing pipeline
- Vector search capabilities
- RAG implementation
- Background task processing
- Monitoring and observability
- Docker deployment

### In Progress 🔄
- Frontend dashboard refinement
- Advanced analytics

### Planned 🔜
- Mobile app support
- Multi-language support
- Advanced ML pipelines

---

**Ready to get started?** Check out the [Quick Start Guide](./docs/01-getting-started/QUICK_START.md)!
