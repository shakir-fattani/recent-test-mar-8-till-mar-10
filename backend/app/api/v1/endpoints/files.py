import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File # type: ignore
from fastapi.responses import FileResponse as ApiFileDownload # type: ignore
from sqlalchemy.orm import Session # type: ignore

from api.deps import get_db, get_current_user
from crud import file as file_crud
from models.user import User
from schemas.file import FileResponse
from core.config import settings

router = APIRouter()

# Base path for file storage - should be configured in settings
FILE_BASE_PATH = settings.UPLOAD_DIR


@router.post("/upload/", response_model=FileResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a file for the current user."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="File has no name")
    
    try:
        # Save file to disk with structured directory
        file_path, file_type, file_size, checksum = file_crud.save_file_to_disk(
            file=file,
            base_path=FILE_BASE_PATH,
            user_id=current_user.id
        )
        
        # Create file record in database
        db_file = file_crud.create_file_record(
            db=db,
            user_id=current_user.id,
            file_name=file.filename,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            file_checksum=checksum
        )
        
        return db_file
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


@router.get("/")
def get_user_files(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all files for the current user."""
    files = file_crud.get_user_files(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return files


@router.get("/{file_id}", response_class=ApiFileDownload)
def download_file(
    file_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download a file by its ID."""
    file = file_crud.get_file_by_id(db=db, file_id=file_id)
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    if file.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this file")
    
    if not os.path.exists(file.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return ApiFileDownload(
        path=file.file_path,
        filename=file.file_name,
        media_type=file.file_type
    )


@router.delete("/{file_id}", response_model=bool)
def delete_file(
    file_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a file by its ID."""
    file = file_crud.get_file_by_id(db=db, file_id=file_id)
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    if file.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this file")
    
    success = file_crud.delete_file(db=db, file_id=file_id)
    return success
