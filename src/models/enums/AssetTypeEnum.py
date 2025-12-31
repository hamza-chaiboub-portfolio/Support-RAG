from enum import Enum


class AssetTypeEnum(str, Enum):
    """Asset type enumeration"""
    
    FILE = "FILE"
    DOCUMENT = "DOCUMENT"
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"