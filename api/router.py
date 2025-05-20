from fastapi import APIRouter

from modules.users.routes import router as user_router
# from modules.documents.routes import router as document_router
# from modules.ingestion.routes import router as ingestion_router

router = APIRouter()
router.include_router(user_router, prefix="/users", tags=["Users"])
# router.include_router(document_router, prefix="/documents", tags=["Documents"])
# router.include_router(ingestion_router, prefix="/ingestion", tags=["Ingestion"])
