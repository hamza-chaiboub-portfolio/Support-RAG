"""Data management routes for file uploads and processing"""

import sys
from pathlib import Path
import logging
import uuid
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from helpers.config import get_settings, Settings
from helpers.database import get_db
from helpers.jwt_handler import verify_token
from models.enums.ResponseSignalEnum import ResponseSignal
from repositories import AssetRepository, ProcessingTaskRepository, ProjectRepository
from controllers.ProcessingController import ProcessingController
from controllers.NLPController import NLPController
from controllers.RAGController import RAGController

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)


@data_router.post("/upload/{project_id}")
async def upload_data(
    project_id: int,
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    app_settings: Settings = Depends(get_settings),
    token: dict = Depends(verify_token)
):
    """
    Upload a data file for a project.
    
    This endpoint accepts file uploads and stores them in a project directory
    and records the asset in the database.
    
    Args:
        project_id: The ID of the project
        file: The file to upload
        db: Database session
        app_settings: Application settings
        
    Returns:
        JSON response with upload status and file ID
    """
    try:
        # Validate file extension
        ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.docx', '.doc', '.md', '.json'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in ALLOWED_EXTENSIONS:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": ResponseSignal.FILE_UPLOAD_FAILED.value}
            )
        
        # Check if project exists
        project_repo = ProjectRepository(db)
        project = await project_repo.get_project(project_id)
        if not project:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"signal": "PROJECT_NOT_FOUND"}
            )
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Create project directory
        project_dir = f"./data/projects/{project_id}"
        os.makedirs(project_dir, exist_ok=True)
        
        # Construct file path
        file_path = os.path.join(project_dir, f"{file_id}{file_ext}")
        
        # Save file
        contents = await file.read()
        with open(file_path, 'wb') as f:
            f.write(contents)
        
        # Determine asset type from file extension
        asset_type_map = {
            '.pdf': 'pdf',
            '.txt': 'text',
            '.md': 'markdown',
            '.docx': 'document',
            '.doc': 'document',
            '.json': 'text'
        }
        asset_type = asset_type_map.get(file_ext, 'document')
        
        # Save asset to database
        asset_repo = AssetRepository(db)
        asset = await asset_repo.create_asset(
            project_id=project_id,
            filename=file.filename,
            asset_type=asset_type,
            file_path=file_path,
            file_size=len(contents)
        )
        
        logger.info(f"File uploaded successfully: {file_id} for project {project_id}")
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                "file_id": file_id,
                "asset_id": asset.id,
                "filename": file.filename,
                "size": len(contents)
            }
        )
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"signal": ResponseSignal.FILE_UPLOAD_FAILED.value}
        )


@data_router.post("/process/{project_id}")
async def process_endpoint(
    project_id: int,
    asset_id: int,
    chunk_size: int = 512,
    overlap_size: int = 50,
    db: AsyncSession = Depends(get_db),
    app_settings: Settings = Depends(get_settings),
    token: dict = Depends(verify_token)
):
    """
    Process a file for chunking and indexing.
    
    This endpoint creates a processing task in the database that can be
    tracked and executed by background workers.
    
    Args:
        project_id: The ID of the project
        asset_id: The ID of the asset to process
        chunk_size: Size of chunks for processing
        overlap_size: Overlap between chunks
        db: Database session
        app_settings: Application settings
        
    Returns:
        JSON response with processing status and task ID
    """
    try:
        # Check if project exists
        project_repo = ProjectRepository(db)
        project = await project_repo.get_project(project_id)
        if not project:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"signal": "PROJECT_NOT_FOUND"}
            )
        
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Create processing task in database
        task_repo = ProcessingTaskRepository(db)
        task = await task_repo.create_task(
            project_id=project_id,
            asset_id=asset_id,
            task_id=task_id
        )
        
        # Trigger synchronous RAG pipeline
        try:
            # 1. Chunking
            processor = ProcessingController(db)
            await processor.process_asset(
                project_id=project_id,
                asset_id=asset_id,
                chunk_size=chunk_size,
                chunk_overlap=overlap_size
            )
            
            # 2. Vectorization
            nlp_controller = NLPController(db)
            await nlp_controller.vectorize_chunks(
                project_id=project_id,
                asset_id=asset_id
            )
            
            # 3. Save to PG Vector
            rag_controller = RAGController(db)
            await rag_controller.save_embeddings_to_db(
                project_id=project_id,
                asset_id=asset_id
            )
            
            # Update task status to completed
            await task_repo.update_task_status(task_id, "completed", progress=100.0)
            
        except Exception as e:
            logger.error(f"Synchronous processing failed: {str(e)}")
            await task_repo.update_task_status(task_id, "failed", error_message=str(e))
            raise e
        
        logger.info(f"Processing completed for asset {asset_id} in project {project_id}")
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "signal": ResponseSignal.PROCESSING_SUCCESS.value,
                "task_id": task_id,
                "status": "processing_queued"
            }
        )
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"signal": "PROCESSING_FAILED"}
        )