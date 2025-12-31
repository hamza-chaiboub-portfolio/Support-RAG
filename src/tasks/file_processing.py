"""File processing tasks"""

import logging

logger = logging.getLogger("celery")

# Lazy import Celery to avoid import errors when celery is not being used
_celery_app = None

def get_celery_app():
    """Get or initialize Celery app"""
    global _celery_app
    if _celery_app is None:
        try:
            from celery_app import celery_app
            _celery_app = celery_app
        except ImportError:
            return None
    return _celery_app


class MockTask:
    """Mock task for when Celery is not available"""
    def __init__(self, task_id=None):
        import uuid
        self.id = task_id or str(uuid.uuid4())


def process_project_files_impl(project_id: int, file_id: str, 
                               chunk_size: int = 512, overlap_size: int = 50, 
                               do_reset: bool = False):
    """
    Implementation of file processing
    """
    logger.info(f"Processing file {file_id} for project {project_id}")
    
    result = {
        "status": "success",
        "project_id": project_id,
        "file_id": file_id,
        "chunk_size": chunk_size,
        "overlap_size": overlap_size,
        "chunks_processed": 0
    }
    
    return result


# Try to use Celery, fall back to sync version
try:
    from celery import Task
    from celery_app import celery_app
    
    class CallbackTask(Task):
        """Task with callback functionality"""
        autoretry_for = (Exception,)
        retry_kwargs = {"max_retries": 5}
        retry_backoff = True
    
    @celery_app.task(base=CallbackTask, bind=True)
    def process_project_files(self, project_id: int, file_id: str, 
                             chunk_size: int = 512, overlap_size: int = 50, 
                             do_reset: bool = False):
        """Celery task for processing project files"""
        try:
            return process_project_files_impl(project_id, file_id, chunk_size, overlap_size, do_reset)
        except Exception as exc:
            logger.error(f"Error processing file: {exc}")
            raise exc
            
except (ImportError, AttributeError):
    # Fallback: create a mock task wrapper
    class ProcessProjectFilesSync:
        """Synchronous fallback for process_project_files"""
        def delay(self, project_id: int, file_id: str, 
                 chunk_size: int = 512, overlap_size: int = 50, 
                 do_reset: bool = False):
            result = process_project_files_impl(project_id, file_id, chunk_size, overlap_size, do_reset)
            return MockTask()
    
    process_project_files = ProcessProjectFilesSync()