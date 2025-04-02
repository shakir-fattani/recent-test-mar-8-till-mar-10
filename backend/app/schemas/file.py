from datetime import datetime
import uuid
from typing import Optional

from pydantic import BaseModel # type: ignore


class FileBase(BaseModel):
    file_name: str
    file_type: str
    file_size: str


class FileCreate(FileBase):
    file_checksum: str


class FileResponse(FileBase):
    id: uuid.UUID
    user_id: int
    file_path: str
    file_checksum: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # Updated from orm_mode = True
