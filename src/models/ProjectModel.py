"""Project model for managing RAG projects"""

from typing import Optional


class Project:
    """Project data class"""
    def __init__(self, project_id: int, project_name: str = "default"):
        self.project_id = project_id
        self.project_name = project_name


class ProjectModel:
    """Project model for database operations"""
    
    def __init__(self, db_client=None):
        self.db_client = db_client
    
    @classmethod
    async def create_instance(cls, db_client=None):
        """Factory method to create model instance"""
        return cls(db_client=db_client)
    
    async def get_project_or_create_one(self, project_id: int) -> Project:
        """Get or create a project by ID"""
        # Placeholder implementation - returns a mock project
        return Project(project_id=project_id, project_name=f"project_{project_id}")