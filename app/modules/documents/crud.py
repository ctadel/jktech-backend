from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, desc, func, select, delete, update
from typing import List, Optional

from sqlalchemy.orm import aliased

from app.common.exceptions import UserNotFoundException
from app.modules.conversations.models import Conversation
from app.modules.documents.models import Document, DocumentStar

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


async def invalidate_document(db: AsyncSession, document_id: int) -> Optional[Document]:
    await db.execute(
        update(Document)
        .where(Document.id == document_id)
        .values(is_active=False)
    )
    await db.commit()

async def invalidate_conversations(db: AsyncSession, document_id: int) -> Optional[Document]:
    await db.execute(
        update(Conversation)
        .where(Conversation.document_id == document_id)
        .values(document_id=None)
    )
    await db.commit()

async def get_document_by_key(db: AsyncSession, doc_key: str) -> Optional[Document]:
    result = await db.execute(
        select(Document).where(
            and_(
                Document.document_key == doc_key,
                Document.is_active == True
            ))
        )
    return result.scalars().first()


async def delete_document(db: AsyncSession, doc_key: str) -> None:
    await db.execute(delete(Document).where(Document.document_key == doc_key))
    await db.commit()


async def get_user_documents(db: AsyncSession, user_id: int) -> List[Document]:
    result = await db.execute(
        select(Document)
        .where(
            Document.user_id == user_id,
            Document.is_active == True
        )
        .order_by(desc(Document.uploaded_at))
    )
    documents = result.scalars().all()

    if not documents:
        return []

    doc_ids = [doc.id for doc in documents]

    star_counts_result = await db.execute(
        select(
            DocumentStar.document_id,
            func.count(DocumentStar.user_id).label("total_stars")
        )
        .where(DocumentStar.document_id.in_(doc_ids))
        .group_by(DocumentStar.document_id)
    )
    star_counts = {row.document_id: row.total_stars for row in star_counts_result}

    # Fetch whether user starred these docs
    user_starred_result = await db.execute(
        select(DocumentStar.document_id)
        .where(
            DocumentStar.user_id == user_id,
            DocumentStar.document_id.in_(doc_ids)
        )
    )
    user_starred_ids = set(user_starred_result.scalars().all())

    for doc in documents:
        setattr(doc, "total_stars", star_counts.get(doc.id, 0))
        setattr(doc, "user_starred", doc.id in user_starred_ids)

    return documents

async def add_views(db: AsyncSession, document_id: int) -> None:
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()

    if document is None:
        raise ValueError("Document not found")

    document.views += 1
    await db.flush()
    await db.commit()


async def get_document_stats(db: AsyncSession, user_id: int):
    total_count_stmt = select(func.count()).select_from(Document).where(
        and_(
            Document.user_id == user_id,
            Document.is_active == True
        )
    )
    total_count_result = await db.execute(total_count_stmt)
    total_documents = total_count_result.scalar_one()

    private_count_stmt = select(func.count()).select_from(Document).where(
        and_(
            Document.user_id == user_id,
            Document.is_active == True,
            Document.is_private_document == True
        )
    )
    private_count_result = await db.execute(private_count_stmt)
    private_documents = private_count_result.scalar_one()

    total_views_stmt = select(func.coalesce(func.sum(Document.views), 0)).where(
        and_(
            Document.user_id == user_id,
            Document.is_active == True
        )
    )
    total_views_result = await db.execute(total_views_stmt)
    total_views = total_views_result.scalar_one()

    total_stars_stmt = select(func.count()).select_from(
        DocumentStar
    ).join(Document).where(
        and_(
            Document.user_id == user_id,
            Document.is_active == True
        )
    )
    total_stars = (await db.execute(total_stars_stmt)).scalar_one()

    total_revisions_stmt = select(func.count()).select_from(Document).where(
        and_(
            Document.user_id == user_id,
            Document.is_active == False
        )
    )
    total_revisions_result = await db.execute(total_revisions_stmt)
    total_revisions = total_revisions_result.scalar_one()

    return {
        "user_id": user_id,
        "total_documents": total_documents,
        "private_documents": private_documents,
        "total_views": total_views,
        "total_stars": total_stars,
        "total_revisions": total_revisions,
    }

async def fetch_explore_documents(db: AsyncSession, user_id: Optional[int], limit: int, offset: int):
    document_query = (
        select(Document)
        .where(
            Document.is_active == True,
            Document.is_private_document == False
        )
        .order_by(desc(Document.views))
        .offset(offset)
        .limit(limit)
    )

    result = await db.execute(document_query)
    documents = result.scalars().all()

    if not documents:
        return []

    doc_ids = [doc.id for doc in documents]

    starred_ids = set()
    if user_id:
        star_result = await db.execute(
            select(DocumentStar.document_id)
            .where(
                DocumentStar.user_id == user_id,
                DocumentStar.document_id.in_(doc_ids)
            )
        )
        starred_ids = set(star_result.scalars().all())

    total_stars_result = await db.execute(
        select(DocumentStar.document_id, func.count(DocumentStar.user_id).label("stars_count"))
        .where(DocumentStar.document_id.in_(doc_ids))
        .group_by(DocumentStar.document_id)
    )
    stars_count_map = {doc_id: count for doc_id, count in total_stars_result.all()}

    for doc in documents:
        setattr(doc, "user_starred", doc.id in starred_ids)
        setattr(doc, "total_stars", stars_count_map.get(doc.id, 0))

    return documents


async def fetch_trending_documents(db: AsyncSession, user_id: int, limit: int, offset: int):
    star_counts_subq = (
        select(
            DocumentStar.document_id,
            func.count(DocumentStar.user_id).label("star_count")
        )
        .group_by(DocumentStar.document_id)
        .order_by(desc("star_count"))
        .limit(limit)
        .offset(offset)
        .subquery()
    )

    documents_stmt = (
        select(Document, star_counts_subq.c.star_count)
        .join(star_counts_subq, Document.id == star_counts_subq.c.document_id)
        .order_by(desc(star_counts_subq.c.star_count))
    )

    result = await db.execute(documents_stmt)
    rows = result.all()

    documents = []
    doc_ids = []
    star_map = {}

    for doc, star_count in rows:
        doc.total_stars = star_count or 0
        documents.append(doc)
        doc_ids.append(doc.id)
        star_map[doc.id] = doc.total_stars

    if user_id and doc_ids:
        user_starred_stmt = (
            select(DocumentStar.document_id)
            .where(
                DocumentStar.user_id == user_id,
                DocumentStar.document_id.in_(doc_ids)
            )
        )
        user_starred_result = await db.execute(user_starred_stmt)
        starred_doc_ids = {row[0] for row in user_starred_result.fetchall()}
    else:
        starred_doc_ids = set()

    for doc in documents:
        doc.user_starred = doc.id in starred_doc_ids
        doc.total_stars = star_map.get(doc.id, 0)

    return documents


async def fetch_latest_documents(db: AsyncSession, user_id: Optional[int], limit: int, offset: int):
    latest_version_subq = (
        select(
            Document.document_key,
            func.max(Document.version).label("latest_version")
        )
        .where(Document.is_private_document == False)
        .group_by(Document.document_key)
        .subquery()
    )

    documents_query = (
        select(Document)
        .join(
            latest_version_subq,
            (Document.document_key == latest_version_subq.c.document_key) &
            (Document.version == latest_version_subq.c.latest_version)
        )
        .order_by(desc(Document.uploaded_at))
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(documents_query)
    documents = result.scalars().all()
    doc_ids = [doc.id for doc in documents]

    starred_doc_ids = set()
    if user_id and doc_ids:
        starred_result = await db.execute(
            select(DocumentStar.document_id)
            .where(
                DocumentStar.user_id == user_id,
                DocumentStar.document_id.in_(doc_ids)
            )
        )
        starred_doc_ids = set(row[0] for row in starred_result.all())

    total_stars_map = {}
    if doc_ids:
        stars_result = await db.execute(
            select(DocumentStar.document_id, func.count().label("count"))
            .where(DocumentStar.document_id.in_(doc_ids))
            .group_by(DocumentStar.document_id)
        )
        total_stars_map = {doc_id: count for doc_id, count in stars_result.all()}

    for doc in documents:
        doc.user_starred = doc.id in starred_doc_ids
        doc.total_stars = total_stars_map.get(doc.id, 0)

    return documents


async def get_document_stars_public(db: AsyncSession, document_id):
    total_stars_stmt = select(func.count()).select_from(DocumentStar).where(Document.id == document_id)
    total_stars_result = await db.execute(total_stars_stmt)
    stars = total_stars_result.scalar_one()
    return {"star_count": stars}

async def get_document_stars(db: AsyncSession, document_id, user_id):
    total_stars = await db.execute(
        select(DocumentStar).where(DocumentStar.document_id == document_id)
    )
    count = total_stars.scalars().all()
    count = len(count)

    user_star_q = await db.execute(
        select(DocumentStar).where(DocumentStar.document_id == document_id, DocumentStar.user_id == user_id)
    )
    user_star = user_star_q.scalars().first() is not None

    return {"total_stars": count, "user_starred": user_star}


async def set_document_stars(db: AsyncSession, document_id: int, user_id: int):
    try:
        star = DocumentStar(user_id=user_id, document_id=document_id)
        db.add(star)
        await db.commit()
    except IntegrityError:
        await db.rollback()
    return {"message": "Star added (if not already starred)"}


async def delete_document_stars(db: AsyncSession, document_id: int, user_id: int):
    try:
        await db.execute(
            delete(DocumentStar).where(
                DocumentStar.user_id == user_id,
                DocumentStar.document_id == document_id
            )
        )
        await db.commit()
    except Exception:
        await db.rollback()
    return {"message": "Star removed (if present)"}
