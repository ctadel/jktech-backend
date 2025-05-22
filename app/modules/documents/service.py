import random
from asyncio import sleep
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, UploadFile, status
from typing import List, Optional
from uuid import uuid4

from app.common.logger import logger
from app.modules.documents import crud
from app.modules.documents.models import Document
from app.modules.documents.storage import LocalStorage
from app.modules.users.models import AccountLevel
from app.common.exceptions import DocumentIngestionException, FreeTierException, InvalidDocumentException

#TODO: use based on environment
storage = LocalStorage()

async def upload_document(
    db: AsyncSession,
    user,
    file: UploadFile,
    title: str,
    is_private: bool,
    document_key: Optional[str] = None,
    is_reupload: bool = False
):
    current_account_type = AccountLevel[user.account_type.upper()]

    user_documents = await crud.get_user_documents(db, user.id)
    if current_account_type <= AccountLevel.BASIC and len(user_documents) >= 3:
        raise FreeTierException("Cannot upload more than 3 documents")

    if is_reupload:
        if current_account_type <= AccountLevel.BASIC:
            raise FreeTierException("Only premium users can reupload (version) documents.")

        existing_versions = await crud.get_documents_by_key(db, document_key)
        if not existing_versions:
            raise InvalidDocumentException("Document key not found for versioning.")
        version = max(doc.version for doc in existing_versions) + 1
    else:
        document_key = str(uuid4())
        version = 1

    file_path = await storage.upload_file(file.file, f"{document_key}_{version}")

    ingestion = await process_document_ingestion(file_path)
    if not ingestion:
        raise DocumentIngestionException('__\(  )/')

    new_doc = await crud.create_document(
        db=db,
        user=user,
        document_key=document_key,
        title=title,
        file_path=file_path,
        version=version,
        is_private=is_private
    )
    return new_doc

async def delete_document(db: AsyncSession, document_id: int, current_user):
    document = await crud.get_document_by_id(db, document_id)
    if not document or document.user_id != current_user.id:
        raise InvalidDocumentException(document_id)
    storage.delete_file(document.file_path)
    await crud.delete_document(db, document_id)

async def list_public_documents(db: AsyncSession, skip: int = 0, limit: int = 10):
    return await crud.get_public_documents(db, skip, limit)

async def list_user_documents(db: AsyncSession, user_id: int):
    return await crud.get_user_documents(db, user_id)

async def get_documents_by_key(db: AsyncSession, key: str):
    return await crud.get_documents_by_key(db, key)

async def get_public_documents_by_user(db: AsyncSession, username: str):
    return await crud.get_public_documents_by_username(db, username)

async def process_document_ingestion(file_path):
    # Simulating the LLM Blackbox call
    delay = random.randint(3, 10)
    await sleep(delay)
    logger.info(f"The LLM took {delay} seconds to ingest the document")
    return True
