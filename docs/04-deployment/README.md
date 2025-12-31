# 🐳 Deployment & DevOps

This section contains deployment guides and operational documentation for running SupportRAG AI in various environments.

## Contents

### [Docker Documentation](./DOCKER.md)
- Docker setup and configuration
- docker-compose usage
- Environment configuration
- Deployment instructions
- Container orchestration
- Service management

---

## 🚀 Deployment Options

### 1. Local Development
```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run development server
uvicorn src.main:app --reload --port 8000
```
- ✅ Easy setup
- ✅ Hot reload enabled
- ✅ Full debugging
- ✅ Good for development

**Use Case:** Development and testing

---

### 2. Docker (Recommended for Production)
```bash
# Build and run with docker-compose
docker-compose -f docker/docker-compose.yml up

# Services included:
# - FastAPI application
# - PostgreSQL database
# - Redis cache
# - Flower monitoring (optional)
```
- ✅ Isolated environment
- ✅ Reproducible across machines
- ✅ Production-ready
- ✅ Easy scaling

**Use Case:** Production and staging

---

### 3. Cloud Deployment
- AWS (EC2, ECS, Lambda)
- Google Cloud (Cloud Run, GKE)
- Azure (App Service, AKS)
- Heroku (Platform as a Service)

---

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] All tests passing (25/25)
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] API documentation reviewed
- [ ] Security scan completed
- [ ] Performance benchmarked

### Deployment
- [ ] Database backup created
- [ ] Docker images built
- [ ] Container health checks enabled
- [ ] Monitoring configured
- [ ] Logging aggregation set up

### Post-Deployment
- [ ] Health check passed
- [ ] API endpoints tested
- [ ] Database connectivity verified
- [ ] Monitoring alerts active
- [ ] Documentation updated

---

## 🔧 Configuration

### Environment Variables Required

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/db

# JWT
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Application
APP_ENV=production
DEBUG=false
```

### Database Setup

**PostgreSQL 12+**
```sql
-- Create database
CREATE DATABASE supportrag;

-- Create user
CREATE USER raguser WITH PASSWORD 'securepassword';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE supportrag TO raguser;
```

---

## 📊 Service Architecture

```
┌─────────────────────────────────┐
│      Load Balancer (nginx)      │
└──────────────┬──────────────────┘
               │
      ┌────────┴────────┐
      │                 │
┌─────▼──┐         ┌────▼───┐
│ API #1 │         │ API #2 │
└─────┬──┘         └────┬───┘
      │                 │
      └────────┬────────┘
               │
         ┌─────▼──────┐
         │ PostgreSQL │
         └────────────┘
               
    ┌──────────────┐
    │ Redis Cache  │
    └──────────────┘
    
    ┌──────────────┐
    │ Flower Logs  │
    └──────────────┘
```

---

## 🔒 Security Considerations

### API Security
- ✅ JWT authentication on all protected endpoints
- ✅ CORS configuration
- ✅ Rate limiting
- ✅ Input validation
- ✅ SQL injection prevention (ORM)

### Database Security
- ✅ Strong passwords
- ✅ Encrypted connections (SSL)
- ✅ User permission restriction
- ✅ Backup encryption
- ✅ Regular updates

### Application Security
- ✅ Secrets management
- ✅ Environment variable protection
- ✅ HTTPS in production
- ✅ Security headers
- ✅ Dependency scanning

---

## 📈 Performance Optimization

### Database
- Connection pooling (20-100 connections)
- Query optimization with indexes
- Regular vacuum and analyze
- Read replicas for scaling

### Application
- Caching with Redis
- Async/await for concurrency
- Load balancing
- CDN for static files

### Monitoring
- Application metrics
- Database performance
- Request/response times
- Error rates
- Resource utilization

---

## 🔍 Monitoring & Logging

### Logs
- **Application logs:** `logs/` directory
- **Docker logs:** `docker logs container_id`
- **Database logs:** PostgreSQL system logs

### Metrics
- Request count and latency
- Error rates
- Database query performance
- Resource usage
- Uptime/availability

### Tools
- **Flower:** Celery task monitoring
- **Grafana:** Metrics visualization
- **Prometheus:** Metrics collection
- **ELK Stack:** Log aggregation

---

## 🚀 Scaling Strategies

### Vertical Scaling
- Increase server resources (CPU, RAM)
- Better for single-instance apps
- Limited by hardware constraints

### Horizontal Scaling
- Multiple API instances behind load balancer
- Database with replication
- Cache layer for performance
- Better for distributed systems

### Database Scaling
- Connection pooling
- Read replicas
- Sharding (if needed)
- Archival of old data

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
```yaml
- Code push to repository
- Run tests (25/25 passing)
- Build Docker image
- Push to registry
- Deploy to staging
- Run integration tests
- Deploy to production
```

**Pipeline Location:** `.github/workflows/deploy-develop.yml`

---

## 📚 Related Documentation

- **Architecture Details:** [Architecture Guide](../02-architecture/)
- **Getting Started:** [Quick Start](../01-getting-started/QUICK_START.md)
- **API Documentation:** Use Swagger at `/docs` after starting app

---

## 🆘 Troubleshooting

### Container Won't Start
```bash
# Check logs
docker logs container_id

# Verify images
docker images

# Rebuild
docker-compose down
docker-compose build --no-cache
```

### Database Connection Failed
```bash
# Test connection
docker exec -it postgres_container psql -U raguser -d supportrag

# Check environment variables
docker inspect container_id | grep ENV
```

### API Not Responding
```bash
# Check if container is running
docker ps

# Verify port mapping
docker port container_id

# Check logs
docker logs -f container_id
```

---

## 🎯 Common Deployment Scenarios

### Local Development
```bash
.\.venv\Scripts\Activate.ps1
uvicorn src.main:app --reload
```

### Docker Development
```bash
docker-compose up
```

### Production Deployment
```bash
docker-compose -f docker/docker-compose.yml up -d
# Monitor with:
docker-compose logs -f
```

---

## 📞 Support & Resources

### Documentation
- [Complete Architecture](../02-architecture/ARCHITECTURE.md)
- [Quick Start Guide](../01-getting-started/QUICK_START.md)
- [Docker Documentation](./DOCKER.md)

### External Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

---

## ✅ Deployment Status

| Environment | Status | URL |
|-------------|--------|-----|
| Development | ✅ Ready | localhost:8000 |
| Docker | ✅ Ready | See docker-compose.yml |
| Production | ⏳ Ready | Configure per deployment |

---

## 🔗 Quick Links

- [Docker Compose File](../../../docker/docker-compose.yml)
- [Environment Examples](../../../docker/env/)
- [Alembic Migrations](../../../docker/rag/alembic.example.ini)