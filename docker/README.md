# SupportRAG AI - Docker Deployment

This directory contains the Docker configuration for deploying the SupportRAG AI application.

## Prerequisites

- Docker Engine
- Docker Compose

## Structure

- `docker-compose.yml`: Main orchestration file
- `rag/Dockerfile`: Dockerfile for the FastAPI application
- `env/`: Environment variable files

## Usage

### 1. Build and Start

```bash
# From the project root
docker-compose -f docker/docker-compose.yml up --build -d
```

### 2. View Logs

```bash
docker-compose -f docker/docker-compose.yml logs -f
```

### 3. Stop Services

```bash
docker-compose -f docker/docker-compose.yml down
```

## Services

- **rag-app**: The FastAPI backend (Port 8000)
- **postgres**: PostgreSQL database with pgvector (Port 5432)
- **redis**: Redis for caching and task queue (Port 6379)

## Configuration

Environment variables are loaded from `docker/env/.env.app`.
You can modify this file to change settings like API keys or database credentials.
