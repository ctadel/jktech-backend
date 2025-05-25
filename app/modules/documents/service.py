import random
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
from app.common.exceptions import DocumentIngestionException, FreeTierException, InvalidDocumentException, InvalidUserParameters
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


    async def _get_username_from_request(self) -> str | None:
        auth = self.request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return None
        token = auth.split(" ")[1]
        try:
            payload = decode_access_token(token)
            username = payload.get("username")
        except: return
        return username

    async def list_user_documents(self, username: str, page: int):

        result = await self.db.execute(select(User).where(User.username == username))
        target_user = result.scalar_one_or_none()
        if not target_user:
            raise InvalidUserParameters(f"User not found: {username}")

        limit, offset = self._get_limit_offset(page)
        active_username = await self._get_username_from_request()

        documents = select(Document).where(Document.user_id == target_user.id)
        if not active_username or active_username != username:
            documents = documents.where(Document.is_private_document == False)

        documents = documents.offset(offset).limit(limit)
        result = await self.db.execute(documents)
        return result.scalars().all()

    async def list_explore_documents(self, page: int):
        limit, offset = self._get_limit_offset(page)

        documents = select(Document).where(Document.is_private_document == False) \
                .offset(offset).limit(limit)
        result = await self.db.execute(documents)
        return result.scalars().all()

    async def list_trending_documents(self, page: int):
        limit, offset = self._get_limit_offset(page)
        documents = select(Document).where(Document.is_private_document == False) \
                .order_by(desc(Document.stars)).offset(offset).limit(limit)

        result = await self.db.execute(documents)
        return result.scalars().all()

    async def list_latest_documents(self, page: int):
        limit, offset = self._get_limit_offset(page)
        documents = select(Document).where(Document.is_private_document == False) \
                .order_by(desc(Document.created_at)).limit(limit).offset(offset)

        result = await self.db.execute(documents)
        return result.scalars().all()


class DocumentService:
    def __init__(self, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
        self.user = user
        self.db = db

    async def process_document(
        self,
        file: UploadFile,
        title: str,
        is_private: bool,
        document_key: Optional[str] = None,
        is_reupload: bool = False
    ):
        current_account_type = AccountLevel[self.user.account_type.upper()]

        user_documents = await crud.get_user_documents(self.db, self.user.id)
        if current_account_type <= AccountLevel.BASIC and len(user_documents) >= FreeTierLimitations.MAX_UPLOAD_DOCUMENTS:
            raise FreeTierException(f"Cannot upload more than {FreeTierLimitations.MAX_UPLOAD_DOCUMENTS} documents")

        if is_reupload:
            if current_account_type <= AccountLevel.BASIC:
                raise FreeTierException("Only premium users can reupload (version) documents.")

            existing_versions = await crud.get_documents_by_key(self.db, document_key)
            if not existing_versions:
                raise InvalidDocumentException("Document key not found for versioning.")
            version = max(doc.version for doc in existing_versions) + 1
        else:
            document_key = str(uuid4())
            version = 1

        file_path = await storage.upload_file(file.file, f"{document_key}_{version}")

        if settings.is_production_server():
            ingestion = await self.process_document_ingestion(file_path)
            if not ingestion:
                raise DocumentIngestionException('__\(  )/__')

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

    async def delete_document(self, document_key: str):
        document = await crud.get_document_by_key(self.db, document_key)
        if not document or document.user_id != self.user.id:
            raise InvalidDocumentException(document_key)
        storage.delete_file(document.file_path)
        await crud.delete_document(self.db, document_key)

    async def process_document_ingestion(file_path):
        # Simulating the LLM Blackbox call
        delay = random.randint(3, 10)
        await sleep(delay)
        logger.info(f"The LLM took {delay} seconds to ingest the document")
        return True


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
