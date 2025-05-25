from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UploadDocumentRequest(BaseModel):
    title: str = 'Harry Potter eBook'
    is_private_document: Optional[bool] = False

class DocumentResponse(BaseModel):
    id: int = 1
    document_key: str = '64aaf05e-1fd3-423b-a564-a3c0200408fd'
    title: str = 'Harry Potter eBook'
    file_path: str = 's3://somesecretlocation/64aaf05e-1fd3-423b-a564-a3c0200408fd'
    version: int = 1
    uploaded_at: datetime = datetime.now()
    is_private_document: bool = False
    user_id: int = 1

class PublicDocumentResponse(BaseModel):
    id: int = 1
    document_key: str = '64aaf05e-1fd3-423b-a564-a3c0200408fd'
    title: str = 'Harry Potter eBook'
    version: int = 2
    uploaded_at: datetime = datetime.now()
    user_id: int = 1

    model_config = {
        "from_attributes": True
    }

class DocumentIngestionStatusResponse(BaseModel):
    document_id: int = 1
    document_key: str = '64aaf05e-1fd3-423b-a564-a3c0200408fd'
    title: str = 'Harry Potter eBook'
    version: int = 2
    uploaded_at: datetime = '2025-11-25 10:42:12'
    ingestion_status: str = 'IN_PROGRESS'

    model_config = {
        "from_attributes": True
    }
