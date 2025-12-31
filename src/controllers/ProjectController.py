"""Project business logic controller"""

import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from helpers.exceptions import (
    ResourceNotFoundException,
    ValidationException,
    DatabaseException,
)
from helpers.logger import setup_logger
from models.db_models import Project, ProjectStatus
from repositories import ProjectRepository
from schemas import ProjectCreateRequest, ProjectUpdateRequest, ProjectResponse

logger = setup_logger(__name__)


class ProjectController:
    """Controller for project-related business logic"""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize project controller
        
        Args:
            db: Database session
        """
        self.db = db
        self.repo = ProjectRepository(db)
        self.logger = logger
    
    async def create_project(self, req: ProjectCreateRequest) -> ProjectResponse:
        """
        Create a new project
        
        Args:
            req: Project creation request
            
        Returns:
            Created project response
            
        Raises:
            ValidationException: If validation fails
            DatabaseException: If database operation fails
        """
        try:
            # Validate input
            if not req.name or len(req.name.strip()) == 0:
                raise ValidationException("Project name cannot be empty", field="name")
            
            self.logger.info(f"Creating project: {req.name}")
            
            # Create project
            project = await self.repo.create_project(
                name=req.name.strip(),
                description=req.description,
                status=ProjectStatus.ACTIVE
            )
            
            self.logger.info(f"Project created successfully: {project.id}")
            return ProjectResponse.from_orm(project)
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Failed to create project: {str(e)}")
            raise DatabaseException(f"Failed to create project: {str(e)}", operation="create")
    
    async def get_project(self, project_id: int) -> ProjectResponse:
        """
        Get project by ID
        
        Args:
            project_id: Project ID
            
        Returns:
            Project response
            
        Raises:
            ResourceNotFoundException: If project not found
            DatabaseException: If database operation fails
        """
        try:
            self.logger.debug(f"Fetching project: {project_id}")
            
            project = await self.repo.get_project(project_id)
            if not project:
                raise ResourceNotFoundException("Project", project_id)
            
            return ProjectResponse.from_orm(project)
            
        except ResourceNotFoundException:
            raise
        except Exception as e:
            self.logger.error(f"Failed to get project {project_id}: {str(e)}")
            raise DatabaseException(f"Failed to retrieve project: {str(e)}", operation="read")
    
    async def list_projects(self, skip: int = 0, limit: int = 10) -> tuple[List[ProjectResponse], int]:
        """
        List all projects with pagination
        
        Args:
            skip: Number of items to skip
            limit: Maximum items to return
            
        Returns:
            Tuple of (projects list, total count)
            
        Raises:
            DatabaseException: If database operation fails
        """
        try:
            # Validate pagination
            if skip < 0:
                skip = 0
            if limit < 1 or limit > 100:
                limit = 10
            
            self.logger.debug(f"Listing projects: skip={skip}, limit={limit}")
            
            projects, total = await self.repo.list_projects(skip=skip, limit=limit)
            
            return [ProjectResponse.from_orm(p) for p in projects], total
            
        except Exception as e:
            self.logger.error(f"Failed to list projects: {str(e)}")
            raise DatabaseException(f"Failed to list projects: {str(e)}", operation="list")
    
    async def update_project(self, project_id: int, req: ProjectUpdateRequest) -> ProjectResponse:
        """
        Update a project
        
        Args:
            project_id: Project ID
            req: Project update request
            
        Returns:
            Updated project response
            
        Raises:
            ResourceNotFoundException: If project not found
            ValidationException: If validation fails
            DatabaseException: If database operation fails
        """
        try:
            # Check if project exists
            project = await self.repo.get_project(project_id)
            if not project:
                raise ResourceNotFoundException("Project", project_id)
            
            # Prepare update data
            update_data = {}
            if req.name is not None:
                if not req.name.strip():
                    raise ValidationException("Project name cannot be empty", field="name")
                update_data["name"] = req.name.strip()
            
            if req.description is not None:
                update_data["description"] = req.description
            
            if req.status is not None:
                update_data["status"] = req.status
            
            if not update_data:
                self.logger.warning(f"No fields to update for project {project_id}")
                return ProjectResponse.from_orm(project)
            
            self.logger.info(f"Updating project {project_id}")
            
            # Update project
            updated_project = await self.repo.update_project(project_id, **update_data)
            
            self.logger.info(f"Project {project_id} updated successfully")
            return ProjectResponse.from_orm(updated_project)
            
        except (ResourceNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Failed to update project {project_id}: {str(e)}")
            raise DatabaseException(f"Failed to update project: {str(e)}", operation="update")
    
    async def delete_project(self, project_id: int) -> bool:
        """
        Delete a project
        
        Args:
            project_id: Project ID
            
        Returns:
            True if deleted successfully
            
        Raises:
            ResourceNotFoundException: If project not found
            DatabaseException: If database operation fails
        """
        try:
            # Check if project exists
            project = await self.repo.get_project(project_id)
            if not project:
                raise ResourceNotFoundException("Project", project_id)
            
            self.logger.info(f"Deleting project {project_id}")
            
            # Delete project (cascades to related assets and chunks)
            await self.repo.delete_project(project_id)
            
            self.logger.info(f"Project {project_id} deleted successfully")
            return True
            
        except ResourceNotFoundException:
            raise
        except Exception as e:
            self.logger.error(f"Failed to delete project {project_id}: {str(e)}")
            raise DatabaseException(f"Failed to delete project: {str(e)}", operation="delete")