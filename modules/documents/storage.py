import os
import shutil
from abc import ABC, abstractmethod
from uuid import uuid4
from fastapi import UploadFile

class Storage(ABC):
    @abstractmethod
    async def upload_file(self, file: UploadFile, filename: str) -> str:
        pass

    @abstractmethod
    async def delete_file(self, filepath: str) -> None:
        pass

class LocalStorage(Storage):
    def __init__(self, base_path: str = "uploads"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    async def upload_file(self, file: UploadFile, filename: str) -> str:
        file_path = os.path.join(self.base_path, f"{filename}")
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file, f)
        return file_path

    async def delete_file(self, filepath: str) -> None:
        if os.path.exists(filepath):
            os.remove(filepath)

class S3Storage(Storage):
    async def upload_file(self, file: UploadFile, filename: str) -> str:
        #TODO: need to implement this while moving to production
        pass

    async def delete_file(self, filepath: str) -> None:
        #TODO: need to implement this while moving to production
        pass
