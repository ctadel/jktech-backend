from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import get_db
from app.common.auth import hash_password, verify_password, create_access_token
from app.common.dependencies import get_current_user, get_db
from app.common.exceptions import InvalidCredentialsException
from app.modules.users import crud
from app.modules.users.models import User
from app.modules.users.schemas import RegisterRequest, UpdateProfileRequest
from app.common.constants import PaginationConstants

class AuthService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    def generate_token(self, user: User) -> str:
        return create_access_token({"username": user.username, "account_type": user.account_type})

    async def activate_current_user(self):
        self.user.is_active = True
        await self.db.commit()

    async def authenticate_user(self, username: str, password: str) -> User:
        user = await crud.get_user_by_username(self.db, username)
        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()
        return user

    async def register_user(self, data: RegisterRequest) -> User:
        hashed_pw = hash_password(data.password)
        return await crud.create_user(self.db, data, hashed_pw)


class UserService:
    def __init__(self, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
        self.user = user
        self.db = db

    async def get_current_profile(self):
        return self.user

    async def update_user_profile(self, data: UpdateProfileRequest) -> User:
        return await crud.update_user(self.db, self.user, data)

    async def update_user_password(self, old_password: str, new_password: str) -> bool:
        if not verify_password(old_password, self.user.hashed_password):
            raise InvalidCredentialsException(status_code=404, detail="Incorrect Old password")
        self.user.hashed_password = hash_password(new_password)
        await self.db.commit()
        return True

    async def update_account_type(self, new_account_type: str) -> User:
        self.user.account_type = new_account_type.account_type
        await self.db.commit()
        await self.db.refresh(self.user)
        return self.user

    async def deactivate_current_user(self):
        self.user.is_active = False
        await self.db.commit()


    ### SUPER ADMIN STUFF ###
    async def list_users(self, page):
        if page < 1: page = 1
        offset = (page - 1) * PaginationConstants.USERS_PER_PAGE
        result = await self.db.execute(select(User)
                       .offset(offset)
                       .limit(PaginationConstants.USERS_PER_PAGE))
        return result.scalars().all()

    async def get_profile(self, username):
        return await crud.get_user_by_username(self.db, username)

    async def deactivate_user_by_user_id(self, user_id: str):
        user = await self.get_user_by_id(user_id)
        user.is_active = False
        await self.db.commit()

    async def delete_user_by_user_id(self, user_id: str):
        user = await self.get_user_by_id(user_id)
        await self.db.delete(user)
        await self.db.commit()
