from enum import Enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.common.database import Base

class IngestionStatus(Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    FAILED = 'failed'
    COMPLETED = 'completed'
    TERMINATED = 'terminated'

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    document_key = Column(String, nullable=False)
    title = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    version = Column(Integer, default=1)
    uploaded_at = Column(DateTime, default=datetime.now)
    is_private_document = Column(Boolean, default=False)

    # Document Activity
    stars = Column(Integer, default=0)
    views = Column(Integer, default=0)

    ingestion_status = Column(String, default=IngestionStatus.PENDING.name, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="documents")
