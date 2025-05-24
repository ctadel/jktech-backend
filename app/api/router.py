from fastapi import APIRouter

from app.modules.users.routes import AuthRoutes, UserProfileRoutes, SuperAdminRoutes
from app.modules.documents.routes import router as document_router

router = APIRouter()

user_router = APIRouter()
user_router.include_router(AuthRoutes('/auth').router)
user_router.include_router(UserProfileRoutes('/profile').router)
user_router.include_router(SuperAdminRoutes('/admin').router)
router.include_router(user_router, prefix='/users')

router.include_router(document_router, prefix="/documents", tags=["Documents"])
