from fastapi import APIRouter

from app.modules.users.routes import AuthRoutes, UserProfileRoutes, SuperAdminRoutes
from app.modules.documents.routes import LLMRoutes, UserDocumentsRoutes, PublicDocumentsRoutes
from app.modules.conversations.routes import ConversationRoutes

router = APIRouter()

user_router = APIRouter()
user_router.include_router(AuthRoutes('/auth').router)
user_router.include_router(UserProfileRoutes('/profile').router)
router.include_router(user_router, prefix='/users')

document_router = APIRouter()
document_router.include_router(UserDocumentsRoutes('/documents').router)
document_router.include_router(PublicDocumentsRoutes('/documents/public').router)
document_router.include_router(LLMRoutes('/llm').router)
router.include_router(document_router)

router.include_router(ConversationRoutes().router)
router.include_router(SuperAdminRoutes('/admin').router)
