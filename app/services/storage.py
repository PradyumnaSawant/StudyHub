import os
import uuid
from abc import ABC, abstractmethod
from fastapi import UploadFile
from app.core.config import settings

class BaseStorageService(ABC):
    @abstractmethod
    async def save_file(self, file: UploadFile) -> str:
        """Saves file and returns public file URL."""
        pass

class LocalStorageService(BaseStorageService):
    def __init__(self, upload_dir: str = settings.UPLOAD_DIR):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    async def save_file(self, file: UploadFile) -> tuple[str, str]:
        """Saves uploaded file locally and returns (relative_file_url, file_size_str)."""
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4().hex[:12]}_{file.filename.replace(' ', '_')}"
        file_path = os.path.join(self.upload_dir, unique_filename)

        contents = await file.read()
        size_bytes = len(contents)
        
        with open(file_path, "wb") as f:
            f.write(contents)

        # Format size string
        if size_bytes < 1024 * 1024:
            size_str = f"{size_bytes / 1024:.1f} KB"
        else:
            size_str = f"{size_bytes / (1024 * 1024):.1f} MB"

        file_url = f"/static/uploads/{unique_filename}"
        return file_url, size_str

# Stub for future Cloud/S3 integration
class S3StorageService(BaseStorageService):
    async def save_file(self, file: UploadFile) -> tuple[str, str]:
        raise NotImplementedError("S3 storage integration configured via S3_BUCKET env variable.")

def get_storage_service() -> BaseStorageService:
    return LocalStorageService()
