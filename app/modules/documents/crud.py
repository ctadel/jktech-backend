from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from app.common.exceptions import UserNotFoundException
from app.modules.documents.models import Document

async def create_document(
    db: AsyncSession,
    user,
    document_key: str,
    title: str,
    file_path: str,
    version: int,
    is_private: bool
) -> Document:
    document = Document(
        user=user,
        document_key=document_key,
        title=title,
        file_path=file_path,
        version=version,
        is_private_document=is_private
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document


async def get_document_by_key(db: AsyncSession, doc_key: str) -> Optional[Document]:
    result = await db.execute(select(Document).where(Document.key == doc_key))
    return result.scalars().first()


async def delete_document(db: AsyncSession, doc_key: str) -> None:
    await db.execute(delete(Document).where(Document.key == doc_key))
    await db.commit()


async def get_user_documents(db: AsyncSession, user_id: int) -> List[Document]:
    result = await db.execute(
        select(Document).where(Document.user_id == user_id)
    )
    return result.scalars().all()


async def get_public_documents(db: AsyncSession, skip: int = 0, limit: int = 10) -> List[Document]:
    result = await db.execute(
        select(Document)
        .where(Document.is_private_document == False)
        .offset(skip)
        .limit(limit)
        .order_by(Document.uploaded_at.desc())
    )
    return result.scalars().all()


async def get_documents_by_key(db: AsyncSession, key: str) -> List[Document]:
    result = await db.execute(
        select(Document).where(Document.document_key == key)
    )
    return result.scalars().all()


async def get_public_documents_by_username(db: AsyncSession, username: str) -> List[Document]:
    # To prevent circular import at module level
    from modules.users.models import User
    from modules.users.crud import get_user_by_username

    user = await get_user_by_username(db, username)
    if not user:
        raise UserNotFoundException()

    result = await db.execute(
        select(Document)
        .join(User)
        .where(User.username == username, Document.is_private_document == False)
    )
    return result.scalars().all()
