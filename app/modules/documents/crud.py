from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Optional

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
