from enum import Enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, UniqueConstraint
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
    is_active = Column(Boolean, default=True)

    # Document Activity
    views = Column(Integer, default=0)

    ingestion_status = Column(String, default=IngestionStatus.PENDING.name, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="documents")
    stars = relationship("DocumentStar", back_populates="document", cascade="all, delete-orphan")


class DocumentStar(Base):
    __tablename__ = "document_stars"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)

    user = relationship("User", back_populates="stars")
    document = relationship("Document", back_populates="stars")

    __table_args__ = (
        UniqueConstraint("user_id", "document_id", name="unique_user_document_star"),
    )
