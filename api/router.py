from fastapi import APIRouter

from modules.users.routes import router as user_router
from modules.documents.routes import router as document_router

router = APIRouter()
router.include_router(user_router, prefix="/users", tags=["Users"])
router.include_router(document_router, prefix="/documents", tags=["Documents"])
