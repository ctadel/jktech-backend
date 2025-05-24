from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UploadDocumentRequest(BaseModel):
    title: str
    is_private_document: Optional[bool] = False

class DocumentResponse(BaseModel):
    id: int
    document_key: str
    title: str
    file_path: str
    version: int
    uploaded_at: datetime
    is_private_document: bool
    user_id: int

class PublicDocumentResponse(BaseModel):
    id: int
    document_key: str
    title: str
    version: int
    uploaded_at: datetime
    user_id: int

    model_config = {
        "from_attributes": True
    }

class DocumentIngestionStatusResponse(BaseModel):
    document_id: int
    document_key: str
    version: int
    title: str
    uploaded_at: str
    ingestion_status: str

    model_config = {
        "from_attributes": True
    }
