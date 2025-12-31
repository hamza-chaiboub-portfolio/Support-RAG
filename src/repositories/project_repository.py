"""Project repository for database operations"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from models.db_models import Project, Asset, Chunk, ProcessingTask, ProjectStatus, AssetType
from datetime import datetime
from typing import Optional, List, Tuple


class ProjectRepository:
    """Repository for project operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_project(self, name: str, description: str = None, status: ProjectStatus = None) -> Project:
        """Create a new project"""
        if status is None:
            status = ProjectStatus.ACTIVE
        project = Project(name=name, description=description, status=status)
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def get_project(self, project_id: int) -> Optional[Project]:
        """Get project by ID"""
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalars().first()

    async def get_all_projects(self, skip: int = 0, limit: int = 100) -> List[Project]:
        """Get all projects with pagination"""
        result = await self.db.execute(
            select(Project).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def list_projects(self, skip: int = 0, limit: int = 10) -> Tuple[List[Project], int]:
        """Get projects with pagination and total count"""
        # Get total count
        count_result = await self.db.execute(select(func.count(Project.id)))
        total = count_result.scalar() or 0
        
        # Get paginated results
        result = await self.db.execute(
            select(Project).offset(skip).limit(limit)
        )
        projects = result.scalars().all()
        return projects, total

    async def update_project(self, project_id: int, **kwargs) -> Optional[Project]:
        """Update project with dynamic fields"""
        project = await self.get_project(project_id)
        if not project:
            return None

        # Update allowed fields
        allowed_fields = {'name', 'description', 'status'}
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                if key == 'status':
                    project.status = ProjectStatus(value) if isinstance(value, str) else value
                else:
                    setattr(project, key, value)
        
        project.updated_at = datetime.utcnow()
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def delete_project(self, project_id: int) -> bool:
        """Delete project"""
        project = await self.get_project(project_id)
        if not project:
            return False

        await self.db.delete(project)
        await self.db.commit()
        return True

    async def get_project_count(self) -> int:
        """Get total project count"""
        result = await self.db.execute(select(Project))
        return len(result.scalars().all())


class AssetRepository:
    """Repository for asset operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_asset(self, project_id: int, filename: str, asset_type: str, 
                          file_path: str = None, file_size: int = None) -> Asset:
        """Create a new asset"""
        asset = Asset(
            project_id=project_id,
            filename=filename,
            asset_type=AssetType(asset_type),
            file_path=file_path,
            file_size=file_size
        )
        self.db.add(asset)
        await self.db.commit()
        await self.db.refresh(asset)
        return asset

    async def get_asset(self, asset_id: int) -> Optional[Asset]:
        """Get asset by ID"""
        result = await self.db.execute(
            select(Asset).where(Asset.id == asset_id)
        )
        return result.scalars().first()

    async def get_project_assets(self, project_id: int, skip: int = 0, limit: int = 100) -> List[Asset]:
        """Get all assets for a project"""
        result = await self.db.execute(
            select(Asset).where(Asset.project_id == project_id).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def mark_as_processed(self, asset_id: int) -> Optional[Asset]:
        """Mark asset as processed"""
        asset = await self.get_asset(asset_id)
        if not asset:
            return None

        asset.is_processed = True
        asset.updated_at = datetime.utcnow()
        self.db.add(asset)
        await self.db.commit()
        await self.db.refresh(asset)
        return asset

    async def delete_asset(self, asset_id: int) -> bool:
        """Delete asset"""
        asset = await self.get_asset(asset_id)
        if not asset:
            return False

        await self.db.delete(asset)
        await self.db.commit()
        return True


class ChunkRepository:
    """Repository for chunk operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_chunk(self, project_id: int, asset_id: int, content: str,
                          chunk_index: int, token_count: int = None) -> Chunk:
        """Create a new chunk"""
        chunk = Chunk(
            project_id=project_id,
            asset_id=asset_id,
            content=content,
            chunk_index=chunk_index,
            token_count=token_count
        )
        self.db.add(chunk)
        await self.db.commit()
        await self.db.refresh(chunk)
        return chunk

    async def get_asset_chunks(self, asset_id: int) -> List[Chunk]:
        """Get all chunks for an asset"""
        result = await self.db.execute(
            select(Chunk).where(Chunk.asset_id == asset_id).order_by(Chunk.chunk_index)
        )
        return result.scalars().all()

    async def get_project_chunks(self, project_id: int, skip: int = 0, limit: int = 100) -> List[Chunk]:
        """Get all chunks for a project"""
        result = await self.db.execute(
            select(Chunk).where(Chunk.project_id == project_id).offset(skip).limit(limit)
        )
        return result.scalars().all()


class ProcessingTaskRepository:
    """Repository for processing task operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_task(self, project_id: int, task_id: str, asset_id: int = None) -> ProcessingTask:
        """Create a new processing task"""
        task = ProcessingTask(
            project_id=project_id,
            asset_id=asset_id,
            task_id=task_id,
            status="pending"
        )
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def get_task(self, task_id: str) -> Optional[ProcessingTask]:
        """Get task by task ID"""
        result = await self.db.execute(
            select(ProcessingTask).where(ProcessingTask.task_id == task_id)
        )
        return result.scalars().first()

    async def update_task_status(self, task_id: str, status: str, progress: float = None, 
                                 error_message: str = None) -> Optional[ProcessingTask]:
        """Update task status"""
        task = await self.get_task(task_id)
        if not task:
            return None

        task.status = status
        if progress is not None:
            task.progress = progress
        if error_message:
            task.error_message = error_message
        task.updated_at = datetime.utcnow()

        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def get_project_tasks(self, project_id: int) -> List[ProcessingTask]:
        """Get all tasks for a project"""
        result = await self.db.execute(
            select(ProcessingTask).where(ProcessingTask.project_id == project_id)
        )
        return result.scalars().all()