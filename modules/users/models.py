from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from enum import IntEnum, auto
from datetime import datetime
from common.database import Base
from modules.documents.models import Document

class AccountLevel(IntEnum):
    """
        With no account
            - gets to (limited) prompt on free available documents
        Basic users
            - Regular signed-up users gets to prompt more free available documents
            - Gets to prompt on self uploaded (limited) documents
        Premium users
            - Gets all the features available
        Moderators
            - Superuser interface to manually intervene (like django-admin dashboard)

    """
    BASIC = auto()  #Free users
    PREMIUM = auto()  #Premium users
    MODERATOR = auto() #Super-user stuff

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=False, nullable=True)
    hashed_password = Column(String, nullable=False)
    account_type = Column(String, default=AccountLevel.BASIC.name, nullable=False)

    # Additional fields
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    documents = relationship(Document, back_populates="owner", cascade="all, delete-orphan")

    class Config:
        extra = "ignore"
