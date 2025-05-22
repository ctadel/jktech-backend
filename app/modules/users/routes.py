from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import get_db
from app.common.exceptions import InvalidCredentialsException, InvalidUserParameters
from app.modules.users import service
from app.modules.users.models import AccountLevel
from app.modules.users.schemas import TokenResponse, UserProfile, LoginRequest, RegisterRequest, \
                                    UpdateProfileRequest, UpdatePasswordRequest, UpgradeAccountRequest
from app.common.dependencies import authorization_level_required, get_current_user

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await service.register_user(db, data)
    token = service.generate_token(user)
    return {"access_token": token}

@router.post("/login", response_model=TokenResponse)
async def login_user(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await service.authenticate_user(db, data.username, data.password)
    token = service.generate_token(user)
    return {"access_token": token}

@router.get("/profile")
async def get_current_user_profile(current_user=Depends(get_current_user)):
    return UserProfile(
        id=str(current_user.id),
        username=current_user.username,
        full_name=current_user.full_name,
        email=current_user.email,
        account_type=current_user.account_type,
        created_at=current_user.created_at
    )

@router.put("/profile")
async def update_profile(
    data: UpdateProfileRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    updated_user = await service.update_user_profile(db, current_user, data)
    return {"message": "Profile updated", "user": updated_user}

@router.put("/password")
async def update_password(
    data: UpdatePasswordRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    success = await service.update_user_password(db, current_user, data.old_password, data.new_password)
    if not success:
        raise InvalidCredentialsException(status_code=400, detail="Old password is incorrect")
    return {"message": "Password updated successfully"}

@router.put("/profile/update-account-type")
async def upgrade_account(
    data: UpgradeAccountRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        account_type = AccountLevel[data.account_type.upper()]
    except KeyError:
        raise InvalidUserParameters(f"account_type = {data.account_type}")

    updated_user = await service.update_account(db, current_user.id, account_type.name)
    return {"message": f"Account upgraded to {account_type.name}", "user": updated_user}


@router.get("/superadmin")
async def get_users(user=Depends(authorization_level_required(AccountLevel.MODERATOR))):
    return {"test": "ok"}
