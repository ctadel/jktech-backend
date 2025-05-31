from fastapi import APIRouter, Form, UploadFile, File, Depends
from typing import List, Optional

from app.common.dependencies import authorization_level_required
from app.modules.users.models import AccountLevel
from app.modules.documents.service import BasicService, DocumentService, IngestionService
from app.modules.documents.schemas import DocumentStatsResponse, DocumentIngestionStatusResponse, DocumentResponse, PublicDocumentResponse
from app.modules.users.schemas import MessageResponse

class UserDocumentsRoutes:
    def __init__(self, prefix: str = "/documents"):
        self.router = APIRouter(
                prefix=prefix, tags=["Documents"],
                dependencies=[authorization_level_required(AccountLevel.BASIC)]
            )
        self.router.get(    ''                              )(self.get_user_documents)
        self.router.post(   ''                              )(self.upload_document)
        self.router.patch(  ''                              )(self.reupload_document)
        self.router.get(    '/stats'                        )(self.get_document_stats)
        self.router.get(    '/{document_key}'               )(self.view_document)
        self.router.delete( '/{document_key}'               )(self.delete_document)

    async def get_user_documents(
            self, service: DocumentService = Depends(DocumentService),
            ) -> List[DocumentResponse]:
        return await service.list_user_documents()

    async def get_document_stats(
            self, service: DocumentService = Depends(DocumentService),
            ) -> DocumentStatsResponse:
        return await service.get_document_stats()

    async def upload_document(
            self,
            title: str = Form(...),
            is_private: bool = Form(False),
            file: UploadFile = File(...),
            service = Depends(DocumentService),
            ) -> DocumentResponse:
        return await service.process_document(
            file=file,
            title=title,
            is_private=is_private
        )

    async def reupload_document(
            self,
            document_key:str = Form(...),
            title: Optional[str] = Form(...),
            is_private: Optional[bool] = Form(...),
            file: UploadFile = File(...),
            service = Depends(DocumentService),
            ) -> DocumentResponse:
        return await service.process_document(
            document_key=document_key,
            file=file,
            title=title,
            is_private=is_private,
        )

    async def view_document(
            self, document_key:str,
            service: DocumentService = Depends(DocumentService),
            ) -> DocumentResponse:
        return await service.get_document(document_key)

    async def delete_document(
        self, document_key: str,
        service: DocumentService = Depends(DocumentService),
    ) -> MessageResponse:
        await service.delete_document(document_key)
        return {'message': 'Document successfully deleted'}


class PublicDocumentsRoutes:
    def __init__(self, prefix: str = "/documents"):
        self.router = APIRouter(
                prefix=prefix, tags=["Public Documents"],
            )
        self.router.get(    '/user/{username}'              )(self.list_user_documents)
        self.router.get(    '/explore'                      )(self.explore_documents)
        self.router.get(    '/explore/trending'             )(self.trending_documents)
        self.router.get(    '/explore/latest'               )(self.latest_documents)

    async def list_user_documents(
            self, username: str,
            page: int = 1,
            service = Depends(BasicService)
            ) -> List[PublicDocumentResponse]:
        documents = await service.list_user_documents(username, page)
        return [PublicDocumentResponse.model_validate(document) for document in documents]

    async def explore_documents(
            self, page: int = 1,
            service = Depends(BasicService)
            ) -> List[PublicDocumentResponse]:
        documents = await service.list_explore_documents(page)
        return [PublicDocumentResponse.model_validate(document) for document in documents]

    async def trending_documents(
            self, page: int = 1,
            service = Depends(BasicService)
            ) -> List[PublicDocumentResponse]:
        documents = await service.list_trending_documents(page)
        return [PublicDocumentResponse.model_validate(document) for document in documents]

    async def latest_documents(
            self, page: int = 1,
            service = Depends(BasicService)
            ) -> List[PublicDocumentResponse]:
        documents = await service.list_latest_documents(page)
        return [PublicDocumentResponse.model_validate(document) for document in documents]

class LLMRoutes:
    def __init__(self, prefix: str = "/llm"):
        self.router = APIRouter(prefix=prefix, tags=["LLM"])

        self.router.get(    '/ingestion_status/{document_id}'   )(self.get_document_status)
        self.router.delete( '/cancel_ingestion/{document_id}'   )(self.stop_document_ingestion)

    async def get_document_status(
            self, document_id:int,
            service = Depends(IngestionService)
            ) -> DocumentIngestionStatusResponse:
        document = await service.get_document_status(document_id)
        return DocumentIngestionStatusResponse.model_validate(document)

    async def stop_document_ingestion(
            self, document_id:int,
            service = Depends(IngestionService)
            ) -> DocumentIngestionStatusResponse:
        document = await service.get_document_status(document_id)
        return DocumentIngestionStatusResponse.model_validate(document)
