APP_NAME="SupportRAG AI"
APP_VERSION="1.0"

JWT_SECRET_KEY="change-this-secret-key"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_HOURS=24

# Database Configuration (Docker)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/supportrag
SQLALCHEMY_ECHO=False

# File handling
FILE_DEFAULT_CHUNK_SIZE=1048576

# LLM Configuration
LLM_PROVIDER="openai"
LLM_API_KEY="your-api-key-here"
LLM_MODEL="gpt-3.5-turbo"

# Embedding Configuration
EMBEDDING_MODEL="sentence-transformers"
VECTOR_STORE_DIR="./chroma_data"
