import random
from faker import Faker
from asyncio import sleep
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Depends, Request, UploadFile
from typing import Optional
from uuid import uuid4

from app.common.database import get_db
from app.common.dependencies import get_current_user, get_optional_user
from app.common.logger import logger
from app.modules.documents import crud
from app.modules.documents.models import Document, IngestionStatus
from app.modules.documents.storage import LocalStorage
from app.modules.users.models import AccountLevel, User
from app.common.exceptions import DocumentIngestionException, DocumentMissingException, FreeTierException, InvalidDocumentException, InvalidUserParameters
from app.config import settings
from app.common.constants import FreeTierLimitations, PaginationConstants
from app.common.auth import decode_access_token

#TODO: use S3/Cloud storage for Production
storage = LocalStorage()

class BasicService:
    def __init__(self, request: Request, db: AsyncSession = Depends(get_db)):
        self.db = db
        self.request = request

    @staticmethod
    def _get_limit_offset(page):
        if page < 1: page = 1
        offset = (page - 1) * PaginationConstants.DOCUMENTS_PER_PAGE
        limit = PaginationConstants.DOCUMENTS_PER_PAGE
        return limit, offset

    async def get_document_stars_public(self, document_id):
        return await crud.get_document_stars_public(self.db, document_id)

    async def list_explore_documents(self, page: int, user_id):
        limit, offset = self._get_limit_offset(page)
        return await crud.fetch_explore_documents(self.db, user_id, limit, offset)

    async def list_trending_documents(self, page: int, user_id):
        limit, offset = self._get_limit_offset(page)
        return await crud.fetch_trending_documents(self.db, user_id, limit, offset)

    async def list_latest_documents(self, page: int, user_id):
        limit, offset = self._get_limit_offset(page)
        return await crud.fetch_latest_documents(self.db, user_id, limit, offset)


class DocumentService:
    def __init__(self, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
        self.user = user
        self.db = db

    async def list_user_documents(self):
        documents = await crud.get_user_documents(self.db, self.user.id)
        return documents

    async def get_document_stats(self):
        response = await crud.get_document_stats(self.db, self.user.id)
        return response

    async def process_document(
        self,
        file: UploadFile,
        title: str,
        is_private: bool,
        document_key: Optional[str] = None,
        is_reupload: bool = False
    ):
        current_account_type = AccountLevel[self.user.account_type.upper()]

        if current_account_type <= AccountLevel.BASIC:
            if is_reupload or document_key:
                raise FreeTierException("Only premium users can reupload (version) documents.")

            stats = await crud.get_document_stats(self.db, self.user.id)
            if  stats.get('total_documents') >= FreeTierLimitations.MAX_UPLOAD_DOCUMENTS:
                raise FreeTierException(f"Cannot upload more than {FreeTierLimitations.MAX_UPLOAD_DOCUMENTS} documents")

        if is_reupload or document_key:
            existing_version = await crud.get_document_by_key(self.db, document_key)

            if not existing_version:
                raise InvalidDocumentException("Document key not found for versioning.")

            await crud.invalidate_document(self.db, existing_version.id)
            await crud.invalidate_conversations(self.db, existing_version.id)

            version = existing_version.version + 1
        else:
            document_key = str(uuid4())
            version = 1

        file_path = await storage.upload_file(file.file, f"{document_key}_{version}")

        new_doc = await crud.create_document(
            db=self.db,
            user=self.user,
            document_key=document_key,
            title=title,
            file_path=file_path,
            version=version,
            is_private=is_private
        )

        return new_doc

    async def get_document(self, document_key: str):
        document = await crud.get_document_by_key(self.db, document_key)
        if not document:
            raise DocumentMissingException(document_key)

        if document.user_id != self.user.id and document.is_private_document:
            raise InvalidDocumentException(document_key)

        stars = await crud.get_document_stars(self.db, document.id, self.user.id)
        document.total_stars = stars.get('total_stars', 0)
        document.user_starred = stars.get('user_starred', 0)

        return document

    async def delete_document(self, document_key: str):
        document = await crud.get_document_by_key(self.db, document_key)
        if not document or document.user_id != self.user.id:
            raise InvalidDocumentException(document_key)
        await storage.delete_file(document.file_path)
        await crud.delete_document(self.db, document_key)

    async def process_document_ingestion(self, file_path):
        # Simulating the LLM Blackbox call
        delay = random.randint(3, 10)
        await sleep(delay)
        logger.info(f"The LLM took {delay} seconds to ingest the document")
        return True

    async def get_document_stars(self, document_id):
        return await crud.get_document_stars(self.db, document_id, self.user_id)

    async def set_document_stars(self, document_id):
        return await crud.set_document_stars(self.db, document_id, self.user.id)

    async def delete_document_stars(self, document_id):
        return await crud.delete_document_stars(self.db, document_id, self.user.id)


class IngestionService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def get_document_status(self, document_id) -> Document:
        document = await self.db.execute(select(Document).where(Document.id  == document_id))
        document = document.scalars().one_or_none()
        if not document:
            raise InvalidDocumentException(document_id)

        if document.ingestion_status in (IngestionStatus.COMPLETED, IngestionStatus.FAILED):
            return document

        logger.debug("Connect to the LLM Server and get the ingestion process")
        logger.debug("Update the latest status in the database")

        response_from_llm = random.choice(list(IngestionStatus))
        document.ingestion_status = response_from_llm.name
        await self.db.commit()
        return document

    @staticmethod
    async def query_document(document_id=None, query=None):
        return Faker().paragraph(random.randrange(1,10))

    async def stop_document_ingestion(self, document_id) -> Document:
        document = await self.db.execute(select(Document).where(Document.id  == document_id)) \
                .scalars().one_or_none()
        if not document:
            raise InvalidDocumentException(document_id)

        if document.ingestion_status in (IngestionStatus.COMPLETED, IngestionStatus.FAILED):
            return document

        logger.debug("Connect to the LLM Server and stopped the ingestion")
        logger.debug("Update the status in the database")

        document.ingestion_status = IngestionStatus.TERMINATED.name
        await self.db.commit()
        return document
