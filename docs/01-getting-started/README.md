# 🚀 Getting Started

Welcome to the SupportRAG AI Getting Started guide. This section will help you set up and run the application quickly.

## Contents

### [Quick Start Guide](./QUICK_START.md)
- **Time Required:** 5 minutes
- Get the application running in minimal time
- Quick API tests with curl commands
- Current status verification

### [Project Overview](./README.md)
- **Time Required:** 10 minutes
- High-level project description
- Technology stack overview
- Project architecture at a glance
- Key features and capabilities

---

## ⚡ Super Quick Start

```bash
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Start the server
uvicorn src.main:app --reload --port 8000

# 3. Visit in browser
http://127.0.0.1:8000/docs
```

**Server will be running at:** http://127.0.0.1:8000

---

## 📚 Next Steps

1. **Start here:** [QUICK_START.md](./QUICK_START.md)
2. **Understand the architecture:** [Full Architecture Guide](../02-architecture/ARCHITECTURE.md)
3. **See what's implemented:** [Phase 2 Complete Report](../03-phase-documentation/PHASE_2_COMPLETED.md)

---

## ✅ Current Status

- ✅ Application fully operational
- ✅ Database connected
- ✅ JWT authentication active
- ✅ All API endpoints working
- ✅ 100% test pass rate

---

## 🔗 Related Documentation

- **Architecture Details:** See [docs/02-architecture/](../02-architecture/)
- **Implementation Progress:** See [docs/03-phase-documentation/](../03-phase-documentation/)
- **Deployment:** See [docs/04-deployment/](../04-deployment/)

---

## 📞 Troubleshooting

### Connection Issues
- Ensure PostgreSQL is running
- Check `.env` file exists in `src/` directory
- Verify DATABASE_URL environment variable

### Port Already in Use
```bash
# Use different port
uvicorn src.main:app --reload --port 8001
```

### Import Errors
- Ensure virtual environment is activated
- Run: `pip install -r src/requirements.txt`

---

## 💡 Tips

- Use the interactive API docs: http://127.0.0.1:8000/docs
- Check logs in `logs/` directory for debugging
- Database tables auto-create on first run