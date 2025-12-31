"""Asset model for managing uploaded files and assets"""

from typing import Optional
from datetime import datetime
from models.db_schemes import Asset
import uuid


class AssetRecord:
    """Asset record response class"""
    def __init__(self, asset_id: int, asset_project_id: int, asset_type: str, 
                 asset_name: str, asset_size: int):
        self.asset_id = asset_id
        self.asset_project_id = asset_project_id
        self.asset_type = asset_type
        self.asset_name = asset_name
        self.asset_size = asset_size
        self.created_at = datetime.now()


class AssetModel:
    """Asset model for database operations"""
    
    def __init__(self, db_client=None):
        self.db_client = db_client
        self._next_asset_id = 1000
    
    @classmethod
    async def create_instance(cls, db_client=None):
        """Factory method to create model instance"""
        return cls(db_client=db_client)
    
    async def create_asset(self, asset: Asset) -> AssetRecord:
        """Create a new asset record"""
        # Placeholder implementation - generates a mock asset ID
        asset_id = self._next_asset_id
        self._next_asset_id += 1
        
        return AssetRecord(
            asset_id=asset_id,
            asset_project_id=asset.asset_project_id,
            asset_type=asset.asset_type,
            asset_name=asset.asset_name,
            asset_size=asset.asset_size
        )