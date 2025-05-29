from fastapi import APIRouter

from app.modules.users.routes import AuthRoutes, UserProfileRoutes, SuperAdminRoutes
from app.modules.documents.routes import LLMRoutes, UserDocumentsRoutes, PublicDocumentsRoutes
from app.modules.conversations.routes import ConversationRoutes
from app.common.constants import Endpoints as EP

router = APIRouter()

user_router = APIRouter()
user_router.include_router(AuthRoutes(EP.Users.Auth.PREFIX).router)
user_router.include_router(UserProfileRoutes(EP.Users.Profile.PREFIX).router)
user_router.include_router(SuperAdminRoutes(EP.Users.SuperAdmin.PREFIX).router)
router.include_router(user_router, prefix=EP.Users.PREFIX)

document_router = APIRouter()
document_router.include_router(UserDocumentsRoutes(EP.Documents.PREFIX).router)
document_router.include_router(PublicDocumentsRoutes(EP.Documents.PublicDocuments.PREFIX).router)
document_router.include_router(LLMRoutes(EP.LLM.PREFIX).router)
router.include_router(document_router)

router.include_router(ConversationRoutes(EP.Conversations.PREFIX).router)
