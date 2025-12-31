"""Unit tests for controllers"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

# We need to add the src directory to path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from controllers.ProjectController import ProjectController
from helpers.exceptions import (
    ResourceNotFoundException,
    ValidationException,
    DatabaseException,
)
from schemas import ProjectCreateRequest, ProjectUpdateRequest


class TestProjectController:
    """Test suite for ProjectController"""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        return AsyncMock(spec=AsyncSession)
    
    @pytest.fixture
    def mock_repo(self):
        """Create mock repository"""
        repo = AsyncMock()
        return repo
    
    @pytest.fixture
    def controller(self, mock_db):
        """Create controller instance with mocked dependencies"""
        with patch('controllers.ProjectController.ProjectRepository'):
            controller = ProjectController(mock_db)
            controller.repo = AsyncMock()
            return controller
    
    @pytest.mark.asyncio
    async def test_create_project_success(self, controller):
        """Test successful project creation"""
        # Arrange
        req = ProjectCreateRequest(name="Test Project", description="Test Description")
        mock_project = MagicMock()
        mock_project.id = 1
        mock_project.name = "Test Project"
        mock_project.description = "Test Description"
        mock_project.status = "active"
        controller.repo.create_project.return_value = mock_project
        
        # Act
        result = await controller.create_project(req)
        
        # Assert
        assert result.name == "Test Project"
        controller.repo.create_project.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_project_empty_name(self, controller):
        """Test project creation with empty name - validation at Pydantic level"""
        # Arrange & Act & Assert
        # Pydantic validates empty name at request creation time
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            req = ProjectCreateRequest(name="", description="Test")
    
    @pytest.mark.asyncio
    async def test_get_project_success(self, controller):
        """Test successful project retrieval"""
        # Arrange
        mock_project = MagicMock()
        mock_project.id = 1
        mock_project.name = "Test Project"
        mock_project.description = "Test Description"
        mock_project.status = "active"
        controller.repo.get_project.return_value = mock_project
        
        # Act
        result = await controller.get_project(1)
        
        # Assert
        assert result.name == "Test Project"
        controller.repo.get_project.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    async def test_get_project_not_found(self, controller):
        """Test project retrieval when project doesn't exist"""
        # Arrange
        controller.repo.get_project.return_value = None
        
        # Act & Assert
        with pytest.raises(ResourceNotFoundException):
            await controller.get_project(999)
    
    @pytest.mark.asyncio
    async def test_list_projects_success(self, controller):
        """Test successful project listing"""
        # Arrange
        mock_project_1 = MagicMock()
        mock_project_1.id = 1
        mock_project_1.name = "Project 1"
        mock_project_1.description = "Desc 1"
        mock_project_1.status = "active"
        
        mock_project_2 = MagicMock()
        mock_project_2.id = 2
        mock_project_2.name = "Project 2"
        mock_project_2.description = "Desc 2"
        mock_project_2.status = "active"
        
        mock_projects = [mock_project_1, mock_project_2]
        controller.repo.list_projects.return_value = (mock_projects, 2)
        
        # Act
        results, total = await controller.list_projects(skip=0, limit=10)
        
        # Assert
        assert len(results) == 2
        assert total == 2
        controller.repo.list_projects.assert_called_once_with(skip=0, limit=10)
    
    @pytest.mark.asyncio
    async def test_update_project_success(self, controller):
        """Test successful project update"""
        # Arrange
        req = ProjectUpdateRequest(name="Updated Name")
        mock_project = MagicMock()
        mock_project.id = 1
        mock_project.name = "Updated Name"
        mock_project.description = "Original Description"
        mock_project.status = "active"
        controller.repo.get_project.return_value = mock_project
        controller.repo.update_project.return_value = mock_project
        
        # Act
        result = await controller.update_project(1, req)
        
        # Assert
        assert result.name == "Updated Name"
        controller.repo.update_project.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_project_not_found(self, controller):
        """Test update of non-existent project"""
        # Arrange
        req = ProjectUpdateRequest(name="Updated Name")
        controller.repo.get_project.return_value = None
        
        # Act & Assert
        with pytest.raises(ResourceNotFoundException):
            await controller.update_project(999, req)
    
    @pytest.mark.asyncio
    async def test_delete_project_success(self, controller):
        """Test successful project deletion"""
        # Arrange
        mock_project = MagicMock()
        controller.repo.get_project.return_value = mock_project
        controller.repo.delete_project.return_value = True
        
        # Act
        result = await controller.delete_project(1)
        
        # Assert
        assert result is True
        controller.repo.delete_project.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    async def test_delete_project_not_found(self, controller):
        """Test deletion of non-existent project"""
        # Arrange
        controller.repo.get_project.return_value = None
        
        # Act & Assert
        with pytest.raises(ResourceNotFoundException):
            await controller.delete_project(999)