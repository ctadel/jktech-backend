from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.common.auth import hash_password, verify_password, create_access_token
from app.modules.users import crud
from app.modules.users.schemas import *
from app.common.exceptions import InvalidCredentialsException
from app.modules.users.models import User
from app.modules.users.schemas import UpdateProfileRequest

async def register_user(db: AsyncSession, data:RegisterRequest):
    #TODO: Implement payment gateway to update the users to premium
    # Meanwhile, we can set up some premium account manually updating the db
    hashed_pw = hash_password(data.password)
    return await crud.create_user(db, data, hashed_pw)

async def update_user_profile(db:AsyncSession, user:User, data: UpdateProfileRequest):
    updated_profile = await crud.update_user(db, user, data)
    return updated_profile

async def update_user_password(db: AsyncSession, user: User, old_password: str, new_password: str):
    if not verify_password(old_password, user.hashed_password):
        return False
    user.hashed_password = hash_password(new_password)
    await db.commit()
    return True

async def authenticate_user(db:AsyncSession, username: str, password: str):
    user = await crud.get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        raise InvalidCredentialsException()
    return user

def generate_token(user):
    return create_access_token({"sub": str(user.id), "account_type": user.account_type})

async def update_account(db: AsyncSession, user_id: str, new_account_type: str):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise InvalidCredentialsException(status_code=404, detail="User not found")

    user.account_type = new_account_type
    await db.commit()
    await db.refresh(user)
    return user
