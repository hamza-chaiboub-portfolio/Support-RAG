from enum import Enum


class ResponseSignal(str, Enum):
    """Response signal enumeration for API responses"""
    
    # File upload signals
    FILE_UPLOAD_SUCCESS = "FILE_UPLOAD_SUCCESS"
    FILE_UPLOAD_FAILED = "FILE_UPLOAD_FAILED"
    
    # Processing signals
    PROCESSING_SUCCESS = "PROCESSING_SUCCESS"
    PROCESS_AND_PUSH_WORKFLOW_READY = "PROCESS_AND_PUSH_WORKFLOW_READY"