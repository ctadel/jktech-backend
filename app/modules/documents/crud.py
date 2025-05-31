from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, desc, func, select, delete
from typing import List, Optional

from sqlalchemy.orm import aliased

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
    result = await db.execute(select(Document).where(Document.document_key == doc_key))
    return result.scalars().first()


async def delete_document(db: AsyncSession, doc_key: str) -> None:
    await db.execute(delete(Document).where(Document.document_key == doc_key))
    await db.commit()


async def get_user_documents(db: AsyncSession, user_id: int) -> List[Document]:
    subquery = (
        select(Document,
                func.row_number().over(
                    partition_by=Document.document_key,
                    order_by=desc(Document.version)
                ).label("rn")
               )
        .where(Document.user_id == user_id)
        .subquery()
    )

    stmt = (
        select(subquery)
        .where(subquery.c.rn == 1)
    )

    result = await db.execute(stmt)
    return result.fetchall()

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


async def add_views(db: AsyncSession, document_id: int) -> None:
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()

    if document is None:
        raise ValueError("Document not found")

    document.views += 1
    await db.flush()
    await db.commit()


async def get_document_stats(db: AsyncSession, user_id: int):
    subquery = (
        select(
            Document.id,
            Document.document_key,
            Document.is_private_document,
            Document.views,
            Document.stars,
            func.row_number().over(
                partition_by=Document.document_key,
                order_by=desc(Document.version)
            ).label("rn")
        )
        .where(Document.user_id == user_id)
        .subquery()
    )

    latest_docs = select(subquery).where(subquery.c.rn == 1).subquery()

    total_count_stmt = select(func.count()).select_from(latest_docs)
    private_count_stmt = select(func.count()).select_from(latest_docs).where(latest_docs.c.is_private_document == True)

    total_count_result = await db.execute(total_count_stmt)
    private_count_result = await db.execute(private_count_stmt)

    total_documents = total_count_result.scalar_one()
    private_documents = private_count_result.scalar_one()

    # Total views and stars from all documents
    misc_stats_stmt = (
        select(
            func.coalesce(func.sum(Document.views), 0).label("total_views"),
            func.coalesce(func.sum(Document.stars), 0).label("total_stars"),
        )
        .where(Document.user_id == user_id)
    )
    misc_stats_result = await db.execute(misc_stats_stmt)
    misc_stats = misc_stats_result.one()

    # Total revisions (version > 1)
    total_revisions_stmt = (
        select(func.count(Document.id))
        .where(and_(Document.user_id == user_id, Document.version > 1))
    )
    total_revisions_result = await db.execute(total_revisions_stmt)
    total_revisions = total_revisions_result.scalar_one()

    return dict(
        user_id = user_id,
        total_documents = total_documents,
        total_views = misc_stats.total_views,
        total_stars = misc_stats.total_stars,
        total_revisions = total_revisions,
        private_documents = private_documents
    )
