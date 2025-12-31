# SupportRAG AI - API Reference Guide

Complete API endpoint documentation with examples.

---

## Table of Contents

1. [Authentication](#authentication)
2. [RAG Pipeline](#rag-pipeline)
3. [File Processing](#file-processing)
4. [NLP Operations](#nlp-operations)
5. [GDPR Compliance](#gdpr-compliance)
6. [API Keys](#api-keys)
7. [Health & Status](#health--status)
8. [Error Handling](#error-handling)
9. [Rate Limiting](#rate-limiting)
10. [Examples](#examples)

---

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All endpoints except public ones require JWT token in the `Authorization` header:

```
Authorization: Bearer <token>
```

---

## Authentication

### Login

**POST** `/auth/login`

Authenticate user and receive JWT token.

#### Request

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "password123"
  }'
```

**Parameters**:
- `username` (string, required): Email or username
- `password` (string, required): User password (minimum 8 characters)

#### Response (200 OK)

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1IiwiZXhwIjoxNzM1Njg5NjAwfQ.7_K8vz...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": 5,
    "email": "user@example.com",
    "username": "user@example.com",
    "full_name": "John Doe"
  }
}
```

#### Error Responses

**401 Unauthorized** - Invalid credentials
```json
{
  "error": "Invalid credentials",
  "code": "INVALID_CREDENTIALS",
  "status": 401
}
```

**400 Bad Request** - Missing fields
```json
{
  "error": "Missing required field: password",
  "code": "MISSING_FIELD",
  "status": 400
}
```

---

## RAG Pipeline

### Query RAG Pipeline

**POST** `/rag/query`

Submit a query to retrieve documents and generate augmented response.

#### Request

```bash
curl -X POST http://localhost:8000/api/v1/rag/query \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "top_k": 5,
    "context_window": 2000,
    "temperature": 0.7
  }'
```

**Parameters**:
- `query` (string, required): The question or search query
- `top_k` (integer, optional, default: 5): Number of documents to retrieve (1-20)
- `context_window` (integer, optional, default: 2000): Maximum context length in tokens
- `temperature` (number, optional, default: 0.7): Response creativity (0.0-1.0)
- `max_tokens` (integer, optional, default: 500): Maximum response length

#### Response (200 OK)

```json
{
  "query": "What is machine learning?",
  "response": "Machine learning is a subset of artificial intelligence (AI) that focuses on developing systems that can learn and improve from experience without being explicitly programmed. These systems use algorithms and statistical models to identify patterns in data...",
  "citations": [
    {
      "document_id": "doc-123",
      "title": "Introduction to Machine Learning",
      "excerpt": "Machine learning enables computers to learn from data and make predictions...",
      "score": 0.95,
      "page": 1
    },
    {
      "document_id": "doc-124",
      "title": "Deep Learning Fundamentals",
      "excerpt": "Deep learning is a subset of machine learning that uses neural networks...",
      "score": 0.87,
      "page": 3
    }
  ],
  "model": "gpt-4",
  "processing_time_ms": 1234,
  "tokens_used": {
    "prompt": 245,
    "completion": 156,
    "total": 401
  }
}
```

#### Error Responses

**400 Bad Request** - Invalid parameters
```json
{
  "error": "top_k must be between 1 and 20",
  "code": "INVALID_PARAMETER",
  "status": 400
}
```

**401 Unauthorized** - Missing/invalid token
```json
{
  "error": "Invalid or missing authorization token",
  "code": "UNAUTHORIZED",
  "status": 401
}
```

**429 Too Many Requests** - Rate limit exceeded
```json
{
  "error": "Rate limit exceeded. Maximum 10 requests per minute",
  "code": "RATE_LIMIT_EXCEEDED",
  "status": 429,
  "retry_after": 45
}
```

---

### Retrieve Documents

**POST** `/rag/retrieve`

Retrieve relevant documents without generating a response.

#### Request

```bash
curl -X POST http://localhost:8000/api/v1/rag/retrieve \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "neural networks",
    "top_k": 10,
    "similarity_threshold": 0.5
  }'
```

**Parameters**:
- `query` (string, required): Search query
- `top_k` (integer, optional, default: 5): Number of results (1-50)
- `similarity_threshold` (number, optional, default: 0.0): Minimum similarity score (0.0-1.0)
- `metadata_filter` (object, optional): Filter by document metadata

#### Response (200 OK)

```json
{
  "query": "neural networks",
  "results": [
    {
      "document_id": "doc-456",
      "title": "Neural Networks in AI",
      "content": "Neural networks are computational systems inspired by biological neural networks...",
      "chunk_id": "chunk-789",
      "similarity_score": 0.96,
      "metadata": {
        "source": "research_paper.pdf",
        "page": 5,
        "date": "2024-01-15"
      }
    },
    {
      "document_id": "doc-457",
      "title": "Deep Learning Architectures",
      "content": "Modern neural networks employ various architectures including...",
      "chunk_id": "chunk-790",
      "similarity_score": 0.91,
      "metadata": {
        "source": "textbook.pdf",
        "page": 42,
        "date": "2024-02-20"
      }
    }
  ],
  "retrieval_time_ms": 234
}
```

---

### Generate Embeddings

**POST** `/rag/embed`

Generate vector embeddings for text.

#### Request

```bash
curl -X POST http://localhost:8000/api/v1/rag/embed \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is the text to embed",
    "model": "text-embedding-3-small"
  }'
```

**Parameters**:
- `text` (string, required): Text to embed
- `model` (string, optional): Embedding model to use

#### Response (200 OK)

```json
{
  "text": "This is the text to embed",
  "embedding": [
    0.02186191, -0.01962757, 0.04358124, -0.00645301, 0.02048127,
    -0.01547529, 0.00456095, 0.01325482, -0.03054825, 0.01734161
  ],
  "model": "text-embedding-3-small",
  "dimension": 1536,
  "usage": {
    "prompt_tokens": 8
  }
}
```

---

### Rerank Documents

**POST** `/rag/rerank`

Rerank retrieved documents based on relevance.

#### Request

```bash
curl -X POST http://localhost:8000/api/v1/rag/rerank \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "what is deep learning",
    "documents": [
      {"id": "doc1", "text": "Deep learning is..."},
      {"id": "doc2", "text": "Neural networks are..."}
    ],
    "top_k": 1
  }'
```

**Parameters**:
- `query` (string, required): Reference query
- `documents` (array, required): Documents to rerank
- `top_k` (integer, optional): Return top K results

#### Response (200 OK)

```json
{
  "results": [
    {
      "document_id": "doc1",
      "relevance_score": 0.98,
      "rank": 1
    },
    {
      "document_id": "doc2",
      "relevance_score": 0.76,
      "rank": 2
    }
  ]
}
```

---

## File Processing

### Upload Document

**POST** `/processing/upload`

Upload a document for processing and indexing.

#### Request

```bash
curl -X POST http://localhost:8000/api/v1/processing/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@document.pdf" \
  -F "title=My Document" \
  -F "tags=important,research"
```

**Parameters**:
- `file` (file, required): Document file (PDF, DOCX, TXT, etc.)
- `title` (string, optional): Document title
- `description` (string, optional): Document description
- `tags` (string, optional): Comma-separated tags
- `metadata` (object, optional): Custom metadata

#### Response (202 Accepted)

```json
{
  "document_id": "doc-abc123",
  "filename": "document.pdf",
  "title": "My Document",
  "size_bytes": 102400,
  "status": "processing",
  "created_at": "2025-01-01T10:30:00Z",
  "processing_status_url": "/api/v1/processing/doc-abc123/status"
}
```

#### Error Responses

**400 Bad Request** - Invalid file
```json
{
  "error": "File type not supported. Supported: PDF, DOCX, TXT, MD",
  "code": "INVALID_FILE_TYPE",
  "status": 400
}
```

**413 Payload Too Large** - File too large
```json
{
  "error": "File size exceeds maximum allowed size of 50MB",
  "code": "FILE_TOO_LARGE",
  "status": 413
}
```

---

### Get Processing Status

**GET** `/processing/{document_id}/status`

Get the processing status of an uploaded document.

#### Request

```bash
curl http://localhost:8000/api/v1/processing/doc-abc123/status \
  -H "Authorization: Bearer <token>"
```

**Parameters**:
- `document_id` (string, path): Document ID from upload response

#### Response (200 OK)

```json
{
  "document_id": "doc-abc123",
  "filename": "document.pdf",
  "status": "completed",
  "progress": 100,
  "chunks_processed": 42,
  "chunks_total": 42,
  "started_at": "2025-01-01T10:30:00Z",
  "completed_at": "2025-01-01T10:35:30Z",
  "processing_time_seconds": 330,
  "error": null
}
```

**Status Values**:
- `pending` - Waiting to be processed
- `processing` - Currently being processed
- `completed` - Successfully processed
- `failed` - Processing failed

---

### Delete Document

**DELETE** `/processing/{document_id}`

Delete a document and all associated chunks.

#### Request

```bash
curl -X DELETE http://localhost:8000/api/v1/processing/doc-abc123 \
  -H "Authorization: Bearer <token>"
```

#### Response (200 OK)

```json
{
  "status": "deleted",
  "document_id": "doc-abc123",
  "chunks_deleted": 42
}
```

---

## NLP Operations

### Vectorize Text

**POST** `/nlp/vectorize`

Convert text to vector representation.

#### Request

```bash
curl -X POST http://localhost:8000/api/v1/nlp/vectorize \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Sample text to vectorize",
    "model": "text-embedding-3-small"
  }'
```

#### Response (200 OK)

```json
{
  "text": "Sample text to vectorize",
  "vector": [0.1, 0.2, -0.3, ...],
  "dimension": 1536,
  "model": "text-embedding-3-small"
}
```

---

### Analyze Sentiment

**POST** `/nlp/sentiment`

Analyze sentiment of text.

#### Request

```bash
curl -X POST http://localhost:8000/api/v1/nlp/sentiment \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This product is amazing and works great!"
  }'
```

#### Response (200 OK)

```json
{
  "text": "This product is amazing and works great!",
  "sentiment": "positive",
  "score": 0.95,
  "confidence": 0.98,
  "details": {
    "positive": 0.95,
    "neutral": 0.04,
    "negative": 0.01
  }
}
```

**Sentiment Values**:
- `positive` - Positive sentiment
- `neutral` - Neutral sentiment
- `negative` - Negative sentiment

---

### Extract Entities

**POST** `/nlp/entities`

Extract named entities from text.

#### Request

```bash
curl -X POST http://localhost:8000/api/v1/nlp/entities \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "John Smith works at Google in Mountain View."
  }'
```

#### Response (200 OK)

```json
{
  "text": "John Smith works at Google in Mountain View.",
  "entities": [
    {
      "text": "John Smith",
      "label": "PERSON",
      "start": 0,
      "end": 10,
      "confidence": 0.99
    },
    {
      "text": "Google",
      "label": "ORG",
      "start": 20,
      "end": 26,
      "confidence": 0.98
    },
    {
      "text": "Mountain View",
      "label": "GPE",
      "start": 30,
      "end": 43,
      "confidence": 0.95
    }
  ]
}
```

---

## GDPR Compliance

### Request Data Export

**POST** `/gdpr/export`

Request user data export.

#### Request

```bash
curl -X POST http://localhost:8000/api/v1/gdpr/export \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "json",
    "include_documents": true
  }'
```

**Parameters**:
- `format` (string, optional): Export format (json, csv, default: json)
- `include_documents` (boolean, optional): Include uploaded documents (default: true)
- `include_chats` (boolean, optional): Include chat history (default: true)

#### Response (202 Accepted)

```json
{
  "export_id": "export-xyz789",
  "status": "processing",
  "user_id": 5,
  "format": "json",
  "estimated_time_minutes": 5,
  "notification_email": "user@example.com",
  "created_at": "2025-01-01T11:00:00Z"
}
```

---

### Get Export Status

**GET** `/gdpr/export/{export_id}`

Get status of data export request.

#### Request

```bash
curl http://localhost:8000/api/v1/gdpr/export/export-xyz789 \
  -H "Authorization: Bearer <token>"
```

#### Response (200 OK)

```json
{
  "export_id": "export-xyz789",
  "status": "completed",
  "format": "json",
  "file_size_bytes": 1024000,
  "download_url": "/api/v1/gdpr/export/export-xyz789/download",
  "expires_at": "2025-01-08T11:00:00Z",
  "created_at": "2025-01-01T11:00:00Z",
  "completed_at": "2025-01-01T11:04:30Z"
}
```

---

### Download Exported Data

**GET** `/gdpr/export/{export_id}/download`

Download exported user data.

#### Request

```bash
curl http://localhost:8000/api/v1/gdpr/export/export-xyz789/download \
  -H "Authorization: Bearer <token>" \
  -o user_data.json
```

#### Response (200 OK)

Binary file download with `Content-Type: application/json`

---

### Request Data Deletion

**POST** `/gdpr/delete`

Request complete user account and data deletion.

#### Request

```bash
curl -X POST http://localhost:8000/api/v1/gdpr/delete \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "confirm": true,
    "reason": "No longer needed"
  }'
```

**Parameters**:
- `confirm` (boolean, required): Confirm deletion (must be true)
- `reason` (string, optional): Reason for deletion

#### Response (202 Accepted)

```json
{
  "deletion_id": "delete-123xyz",
  "status": "processing",
  "user_id": 5,
  "estimated_time_minutes": 15,
  "notification_email": "user@example.com",
  "created_at": "2025-01-01T12:00:00Z"
}
```

---

### Get Deletion Status

**GET** `/gdpr/delete/{deletion_id}`

Get status of data deletion request.

#### Request

```bash
curl http://localhost:8000/api/v1/gdpr/delete/delete-123xyz \
  -H "Authorization: Bearer <token>"
```

#### Response (200 OK)

```json
{
  "deletion_id": "delete-123xyz",
  "status": "completed",
  "records_deleted": 1234,
  "documents_deleted": 42,
  "started_at": "2025-01-01T12:00:00Z",
  "completed_at": "2025-01-01T12:15:00Z"
}
```

---

## API Keys

### Create API Key

**POST** `/api-keys/create`

Create a new API key for programmatic access.

#### Request

```bash
curl -X POST http://localhost:8000/api/v1/api-keys/create \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production API Key",
    "scopes": ["read:rag", "write:documents"],
    "expires_in_days": 365
  }'
```

**Parameters**:
- `name` (string, required): Friendly name for the key
- `scopes` (array, optional): Permissions
- `expires_in_days` (integer, optional): Days until expiration

#### Response (201 Created)

```json
{
  "key_id": "key-abc123",
  "key": "sk_live_abc123def456ghi789jkl...",
  "name": "Production API Key",
  "scopes": ["read:rag", "write:documents"],
  "created_at": "2025-01-01T13:00:00Z",
  "expires_at": "2026-01-01T13:00:00Z",
  "last_used_at": null
}
```

⚠️ **Important**: Store the key in a secure location. It won't be shown again!

---

### List API Keys

**GET** `/api-keys`

List all API keys for current user.

#### Request

```bash
curl http://localhost:8000/api/v1/api-keys \
  -H "Authorization: Bearer <token>"
```

#### Response (200 OK)

```json
{
  "keys": [
    {
      "key_id": "key-abc123",
      "name": "Production API Key",
      "created_at": "2025-01-01T13:00:00Z",
      "expires_at": "2026-01-01T13:00:00Z",
      "last_used_at": "2025-01-02T10:30:00Z",
      "is_active": true
    }
  ]
}
```

---

### Revoke API Key

**DELETE** `/api-keys/{key_id}`

Revoke an API key.

#### Request

```bash
curl -X DELETE http://localhost:8000/api/v1/api-keys/key-abc123 \
  -H "Authorization: Bearer <token>"
```

#### Response (200 OK)

```json
{
  "status": "revoked",
  "key_id": "key-abc123"
}
```

---

## Health & Status

### Health Check

**GET** `/health`

Check application health status (public endpoint).

#### Request

```bash
curl http://localhost:8000/api/v1/health
```

#### Response (200 OK)

```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T14:00:00Z",
  "version": "2.0",
  "uptime_seconds": 3600,
  "database": {
    "status": "connected",
    "latency_ms": 2
  },
  "cache": {
    "status": "connected",
    "latency_ms": 1
  },
  "vector_db": {
    "status": "connected",
    "latency_ms": 5
  }
}
```

---

### Application Info

**GET** `/`

Get application information (public endpoint).

#### Request

```bash
curl http://localhost:8000/api/v1/
```

#### Response (200 OK)

```json
{
  "name": "SupportRAG AI",
  "version": "2.0",
  "environment": "production",
  "api_version": "v1",
  "description": "FastAPI-based RAG Application",
  "docs_url": "/api/docs"
}
```

---

### Application Metrics

**GET** `/metrics`

Get application metrics (requires authentication).

#### Request

```bash
curl http://localhost:8000/api/v1/metrics \
  -H "Authorization: Bearer <token>"
```

#### Response (200 OK)

```json
{
  "requests": {
    "total": 15234,
    "per_second": 2.1,
    "by_method": {
      "GET": 8120,
      "POST": 6950,
      "PUT": 145,
      "DELETE": 19
    },
    "by_endpoint": {
      "/rag/query": 5234,
      "/auth/login": 450,
      "/processing/upload": 234
    }
  },
  "response_time": {
    "average_ms": 145,
    "p50_ms": 98,
    "p95_ms": 450,
    "p99_ms": 1200
  },
  "errors": {
    "4xx": 45,
    "5xx": 2,
    "error_rate": 0.003
  },
  "active_sessions": 23,
  "cache_hit_rate": 0.78
}
```

---

## Error Handling

### Standard Error Response

All errors follow this format:

```json
{
  "error": "Descriptive error message",
  "code": "ERROR_CODE",
  "status": 400,
  "timestamp": "2025-01-01T14:30:00Z",
  "request_id": "req-123456",
  "details": {}
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `INVALID_CREDENTIALS` | 401 | Invalid username/password |
| `UNAUTHORIZED` | 401 | Missing/invalid token |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `INVALID_PARAMETER` | 400 | Invalid request parameter |
| `VALIDATION_ERROR` | 422 | Request validation failed |
| `RATE_LIMIT_EXCEEDED` | 429 | Rate limit exceeded |
| `INTERNAL_ERROR` | 500 | Server error |

---

## Rate Limiting

Endpoints are rate-limited to prevent abuse:

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/auth/login` | 5 | 15 minutes |
| `/rag/query` | 10 | 1 minute |
| `/processing/upload` | 20 | 1 hour |
| Other endpoints | 100 | 1 hour |

When rate limited, response includes:
```
Retry-After: 45
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1735689600
```

---

## Examples

### Complete RAG Query Flow

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user@example.com","password":"password123"}' \
  | jq -r '.access_token')

# 2. Upload document
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/processing/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@document.pdf" \
  -F "title=My Document")

DOCUMENT_ID=$(echo $RESPONSE | jq -r '.document_id')

# 3. Wait for processing (poll status)
until [ "$(curl -s http://localhost:8000/api/v1/processing/$DOCUMENT_ID/status \
  -H "Authorization: Bearer $TOKEN" | jq -r '.status')" = "completed" ]; do
  echo "Processing..."
  sleep 2
done

# 4. Query RAG pipeline
curl -X POST http://localhost:8000/api/v1/rag/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main topic?",
    "top_k": 5
  }' | jq .
```

### Using API Key

```bash
# Create API key
API_KEY=$(curl -s -X POST http://localhost:8000/api/v1/api-keys/create \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"My App"}' | jq -r '.key')

# Use API key in requests
curl -X POST http://localhost:8000/api/v1/rag/query \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"What is RAG?"}'
```

---

## OpenAPI / Swagger

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

---

**Last Updated**: December 2025  
**API Version**: v1  
**Status**: Production Ready
