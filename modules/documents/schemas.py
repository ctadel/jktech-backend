from pydantic import BaseModel
from datetime import datetime

class DocumentUpload(BaseModel):
    filename: str
    is_public: bool = False

class DocumentResponse(BaseModel):
    id: int
    filename: str
    version: int
    is_public: bool
    uploaded_at: datetime

    class Config:
        orm_mode = True
