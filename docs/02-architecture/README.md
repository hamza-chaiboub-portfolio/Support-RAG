# 🏗️ Architecture & Design

This section contains detailed documentation about the application's architecture, design patterns, and implementation details.

## Contents

### 📌 [Complete Architecture Guide](./ARCHITECTURE.md) - **START HERE**
- **Time Required:** 20-30 minutes
- Comprehensive architecture explanation
- System design diagrams and flows
- How all components work together
- Current development status
- Technology stack details
- API endpoints documentation
- Roadmap and next phases
- Database schema

**This is the most comprehensive document. Read this to understand everything about the system.**

---

### 📋 Architecture Implementation Details

#### [Architecture Update Manifest](./ARCHITECTURE_UPDATE_MANIFEST.md)
- Detailed list of everything implemented
- Component organization and structure
- Files and their purposes
- Related documentation references
- Implementation checklist

#### [Architecture Update Checklist](./ARCHITECTURE_UPDATE_CHECKLIST.md)
- Verification of completed tasks
- Component status checks
- Testing status
- Integration status

#### [Architecture Update Summary](./ARCHITECTURE_UPDATE_SUMMARY.txt)
- Quick summary of latest updates
- Key achievements and milestones
- Overview of features

#### [Architecture Update Complete](./ARCHITECTURE_UPDATE_COMPLETE.txt)
- Completion status report
- Final verification results

---

## 🏛️ Architecture Overview

### Layered Architecture

```
┌─────────────────────────────────────┐
│     API Routes Layer (HTTP)         │ ← Client requests
├─────────────────────────────────────┤
│    Authentication Layer (JWT)       │ ← Security
├─────────────────────────────────────┤
│   Business Logic Layer (Ctrl)       │ ← Core logic
├─────────────────────────────────────┤
│  Data Access Layer (Repository)     │ ← DB abstraction
├─────────────────────────────────────┤
│  ORM & Database Layer (SQLAlchemy)  │ ← Persistence
├─────────────────────────────────────┤
│     PostgreSQL Database             │ ← Data storage
└─────────────────────────────────────┘
```

### Key Technologies

| Component | Tech | Version |
|-----------|------|---------|
| **Web Framework** | FastAPI | 0.110.2 |
| **ASGI Server** | Uvicorn | 0.29.0 |
| **Authentication** | PyJWT | 2.10.1 |
| **Database** | PostgreSQL | 12+ |
| **ORM** | SQLAlchemy | 2.0.36 |
| **Async Driver** | asyncpg | 0.30.0 |

---

## 📊 Database Schema

### Core Tables

**projects** - RAG project containers
```
id (UUID)
name (VARCHAR)
description (TEXT)
status (ENUM: ACTIVE, INACTIVE, ARCHIVED)
created_at, updated_at
```

**assets** - File uploads
```
id (UUID)
project_id (FK)
filename (VARCHAR)
asset_type (ENUM: PDF, TEXT, MARKDOWN, DOCUMENT)
file_path (TEXT)
file_size (INTEGER)
is_processed (BOOLEAN)
created_at, updated_at
```

**chunks** - Text chunks
```
id (UUID)
asset_id (FK)
project_id (FK)
content (TEXT)
chunk_index (INTEGER)
token_count (INTEGER)
embedding_vector (VECTOR)
created_at, updated_at
```

**processing_tasks** - Background jobs
```
id (UUID)
project_id (FK)
asset_id (FK)
task_id (VARCHAR - Celery ID)
status (VARCHAR)
progress (INTEGER)
error_message (TEXT)
created_at, updated_at
```

---

## 🔄 How It All Works Together

1. **Client** sends HTTP request to API endpoint
2. **Routes** layer validates request format
3. **JWT Handler** verifies authentication token
4. **Controllers** execute business logic
5. **Repositories** abstract database queries
6. **SQLAlchemy ORM** maps objects to SQL
7. **PostgreSQL** stores and retrieves data
8. **Response** flows back through layers
9. **Client** receives JSON result

---

## 🎯 Design Patterns Used

### Repository Pattern
- Abstracts database queries
- Makes testing easier
- Centralizes data access logic
- Enables easy database swaps

### Dependency Injection
- Controllers depend on repositories
- Repositories depend on database
- FastAPI handles injection automatically
- Improves testability

### Layered Architecture
- Clear separation of concerns
- Each layer has single responsibility
- Easy to modify one layer without affecting others
- Standard industry pattern

### Async/Await
- Non-blocking database operations
- Better performance with many concurrent users
- Built into FastAPI and SQLAlchemy 2.0
- Enables Celery task integration

---

## 📖 What to Read Next

1. **First time?** → [Complete Architecture Guide](./ARCHITECTURE.md)
2. **Need details?** → [Manifest](./ARCHITECTURE_UPDATE_MANIFEST.md)
3. **Getting started?** → [Quick Start Guide](../01-getting-started/QUICK_START.md)
4. **Want status?** → [Phase 2 Complete](../03-phase-documentation/PHASE_2_COMPLETED.md)

---

## 🔍 Quick Reference

### Important Files by Function

**Configuration & Setup**
- `src/helpers/config.py` - Settings management
- `src/helpers/database.py` - Database connection

**Authentication**
- `src/helpers/jwt_handler.py` - JWT token handling

**Data Models**
- `src/models/db_models.py` - ORM models
- `src/schemas/project.py` - Project schemas
- `src/schemas/asset.py` - Asset schemas

**Business Logic**
- `src/controllers/ProjectController.py` - Project operations
- `src/controllers/DataController.py` - File operations

**Data Access**
- `src/repositories/project_repository.py` - All repositories

**API Endpoints**
- `src/routes/base.py` - Main routes
- `src/routes/auth.py` - Authentication routes

---

## ✅ Phase Status

- ✅ Phase 1: Foundation
- ✅ Phase 2: Core Features & Database
- 🔜 Phase 3: RAG Pipeline
- 🔜 Phase 4: Vector Database
- 🔜 Phase 5: LLM Integration

---

## 💡 Key Concepts

**RAG (Retrieval-Augmented Generation)**
- Combines document retrieval with LLM inference
- Provides context to language models
- Enables better answers with specific knowledge

**Repository Pattern**
- Data access abstraction layer
- Makes database queries centralized
- Easier to test and maintain

**JWT Authentication**
- Stateless token-based security
- Token contains user information
- No session storage needed

**Async/Await**
- Non-blocking I/O operations
- Better resource utilization
- Handles many concurrent requests

---

## 🚀 Next Steps

- Read the [Complete Architecture Guide](./ARCHITECTURE.md) for deep dive
- Check [Phase 2 Status](../03-phase-documentation/PHASE_2_COMPLETED.md) for current progress
- Review [API Documentation](../01-getting-started/README.md#api-endpoints) for available endpoints