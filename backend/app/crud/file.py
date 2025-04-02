import uuid
import os
import hashlib
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session # type: ignore
from fastapi import UploadFile # type: ignore

from models.file import FileList


def save_file_to_disk(
    file: UploadFile,
    base_path: str,
    user_id: int
) -> Tuple[str, str, int, str]:
    """
    Save the file to disk with the structured directory system:
    {basePath}/{user_id}/{year}/{month}/{weekNo}/{random-name with uuid}
    
    Returns the file_path, file_type, file_size, and checksum.
    """
    # Get current date info
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    # Calculate week number (1-52)
    week_no = now.isocalendar()[1]
    
    # Create random filename with original extension
    original_filename = file.filename
    file_extension = os.path.splitext(original_filename)[1] if original_filename else ""
    random_filename = f"{uuid.uuid4()}-{file.filename}"
    
    # Create directory structure
    dir_path = os.path.join(base_path, str(user_id), year, month, str(week_no))
    os.makedirs(dir_path, exist_ok=True)
    
    # Full file path
    file_path = os.path.join(dir_path, random_filename)
    
    # Save file to disk
    content = file.file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Calculate file size
    file_size = len(content)
    
    # Calculate checksum for security
    checksum = hashlib.md5(content).hexdigest()
    
    # Get file type (mime type or extension)
    file_type = file.content_type or file_extension.lstrip(".")
    
    return file_path, file_type, file_size, checksum


def create_file_record(
    db: Session,
    user_id: int,
    file_name: str,
    file_path: str,
    file_type: str,
    file_size: int,
    file_checksum: str
) -> FileList:
    """Create a file record in the database."""
    db_file = FileList(
        user_id=user_id,
        file_name=file_name,
        file_path=file_path,
        file_type=file_type,
        file_size=str(file_size),
        file_checksum=file_checksum
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


def get_user_files(
    db: Session, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[FileList]:
    """Get all files for a specific user."""
    return db.query(FileList).filter(
        FileList.user_id == user_id
    ).order_by(
        FileList.created_at.desc()
    ).offset(skip).limit(limit).all()


def get_file_by_id(
    db: Session, 
    file_id: uuid.UUID
) -> Optional[FileList]:
    """Get a file by its ID."""
    return db.query(FileList).filter(FileList.id == file_id).first()


def delete_file(
    db: Session, 
    file_id: uuid.UUID
) -> bool:
    """Delete a file record and remove it from disk."""
    file = db.query(FileList).filter(FileList.id == file_id).first()
    if not file:
        return False
    
    # Delete the file from disk if it exists
    if os.path.exists(file.file_path):
        try:
            os.remove(file.file_path)
        except (OSError, PermissionError):
            # Log the error but continue with db deletion
            pass
    
    # Delete from database
    db.delete(file)
    db.commit()
    return True
