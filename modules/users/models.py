from sqlalchemy import Column, Integer, String, Enum as SqlEnum, DateTime
from sqlalchemy.orm import relationship
from enum import Enum
from datetime import datetime
from common.database import Base

class UserRole(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SqlEnum(UserRole), default=UserRole.VIEWER)

    # Additional fields
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")
