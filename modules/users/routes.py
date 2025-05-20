from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from common.database import get_db
from modules.users import service, crud
from modules.users.schemas import *
from common.dependencies import get_current_user, require_role

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await service.register_user(db, data.username, data.password)
    token = service.generate_token(user)
    return {"access_token": token}

@router.post("/login", response_model=TokenResponse)
async def login_user(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await service.authenticate_user(db, data.username, data.password)
    token = service.generate_token(user)
    return {"access_token": token}

@router.post("/role", dependencies=[Depends(require_role("admin"))])
async def update_role(data: RoleUpdateRequest, db: AsyncSession = Depends(get_db)):
    return crud.update_user_role(db, data.user_id, data.role)

@router.get("/me")
async def get_current_user_profile(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
    }
