"""SQLAlchemy ORM models for database"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from helpers.database import Base
import enum
import json
from sqlalchemy.types import TypeDecorator


class VectorFallback(TypeDecorator):
    """Fallback type for vector storage when pgvector is not available"""
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, list):
            return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        try:
            return json.loads(value)
        except:
            return value


class ProjectStatus(str, enum.Enum):
    """Project status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class AssetType(str, enum.Enum):
    """Asset type enumeration"""
    PDF = "pdf"
    TEXT = "text"
    MARKDOWN = "markdown"
    DOCUMENT = "document"


class Project(Base):
    """Project model - represents a RAG project"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assets = relationship("Asset", back_populates="project", cascade="all, delete-orphan")
    chunks = relationship("Chunk", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name})>"


class Asset(Base):
    """Asset model - represents a file asset in a project"""
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    asset_type = Column(SQLEnum(AssetType), nullable=False)
    file_path = Column(String(512), nullable=True)
    file_size = Column(Integer, nullable=True)  # in bytes
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="assets")
    chunks = relationship("Chunk", back_populates="asset", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Asset(id={self.id}, filename={self.filename}, project_id={self.project_id})>"


class Chunk(Base):
    """Chunk model - represents a text chunk extracted from an asset"""
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Order of chunk within asset
    token_count = Column(Integer, nullable=True)
    embedding_vector = Column(VectorFallback, nullable=True)  # Fallback to Text storage
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="chunks")
    asset = relationship("Asset", back_populates="chunks")

    def __repr__(self):
        return f"<Chunk(id={self.id}, asset_id={self.asset_id}, chunk_index={self.chunk_index})>"


class ProcessingTask(Base):
    """Processing task model - tracks file processing tasks"""
    __tablename__ = "processing_tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=True)
    task_id = Column(String(255), unique=True, nullable=False, index=True)  # Celery task ID
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    progress = Column(Float, default=0.0)  # 0-100
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ProcessingTask(id={self.id}, task_id={self.task_id}, status={self.status})>"