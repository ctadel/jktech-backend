from fastapi import APIRouter, Form, UploadFile, File, Depends
from typing import List, Optional

from app.common.endpoints import BASE_ENDPOINT as EP
from app.common.dependencies import authorization_level_required
from app.modules.users.models import AccountLevel
from app.modules.documents.service import BasicService, DocumentService, IngestionService
from app.modules.documents.schemas import DocumentIngestionStatusResponse, DocumentResponse, PublicDocumentResponse
from app.modules.users.schemas import MessageResponse

class UserDocumentsRoutes:
    def __init__(self, prefix: str = "/documents"):
        self.router = APIRouter(
                prefix=prefix, tags=["Documents"],
                dependencies=[authorization_level_required(AccountLevel.BASIC)]
            )
        self.router.post(   EP.Documents.UPLOAD_DOCUMENT              )(self.upload_document)
        self.router.patch(  EP.Documents.REUPLOAD_DOCUMENT            )(self.reupload_document)
        self.router.get(    EP.Documents.VIEW_DOCUMENT                )(self.view_document)
        self.router.delete( EP.Documents.DELETE_DOCUMENT              )(self.delete_document)

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
            service = Depends(DocumentService),
            ) -> DocumentResponse:
        return await service.get_document(document_key)

    async def delete_document(
        self, document_key: str,
        service = Depends(DocumentService),
    ) -> MessageResponse:
        await service.delete_document(document_key)
        return {'message': 'Document successfully deleted'}


class PublicDocumentsRoutes:
    def __init__(self, prefix: str = "/documents"):
        self.router = APIRouter(
                prefix=prefix, tags=["Public Documents"],
            )
        endponints = EP.Documents.PublicDocuments

        self.router.get(    endponints.LIST_USER_DOCUMENTS            )(self.list_user_documents)
        self.router.get(    endponints.EXPLORE_DOCUMENTS              )(self.explore_documents)
        self.router.get(    endponints.TRENDING_DOCUMENTS             )(self.trending_documents)
        self.router.get(    endponints.LATEST_DOCUMENTS               )(self.latest_documents)

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

        self.router.get(    EP.LLM.GET_DOCUMENT_STATUS                )(self.get_document_status)
        self.router.delete( EP.LLM.STOP_DOCUMENT_INGESTION            )(self.stop_document_ingestion)

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
