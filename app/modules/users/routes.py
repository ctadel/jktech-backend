from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.common.dependencies import authorization_level_required
from app.modules.users.models import AccountLevel
from app.modules.users.schemas import TokenResponse, LoginRequest, RegisterRequest, UpdateProfileResponse, UpdateProfileRequest, \
        UpdatePasswordRequest, UpgradeAccountRequest, UserProfile, MessageResponse
from app.modules.users.service import AuthService, UserService

class AuthRoutes:
    def __init__(self, prefix: str = "/auth"):
        self.router = APIRouter(prefix=prefix, tags=["Auth"])

        self.router.post(   '/register'                     )(self.register)
        self.router.post(   '/login'                        )(self.login)
        self.router.post(   '/token',                       )(self.get_token)

    async def register(self, data: RegisterRequest, service:AuthService = Depends(AuthService)) -> TokenResponse:
        user = await service.register_user(data)
        token = service.generate_token(user)
        return {"access_token": token}

    async def login(self, data: LoginRequest, service:AuthService = Depends(AuthService)) -> TokenResponse:
        user = await service.authenticate_user(data.username, data.password)
        token = service.generate_token(user)
        return {"access_token": token}

    async def get_token(
            self, form_data: OAuth2PasswordRequestForm = Depends(),
            service:AuthService = Depends(AuthService)
            ):
        user = await service.authenticate_user(form_data.username, form_data.password)
        token = service.generate_token(user)
        return {"access_token": token}


class UserProfileRoutes:
    def __init__(self, prefix: str = '/profile'):
        self.router = APIRouter(prefix=prefix, tags=["User"])

        self.router.get(    ''                              )(self.get_user_profile)
        self.router.patch(  '/update'                       )(self.update_profile)
        self.router.patch(  '/account/update-password'      )(self.update_password)
        self.router.post(   '/account/update-account-type'  )(self.update_account_type)
        self.router.post(   '/account/activate'             )(self.deactivate_profile)
        self.router.delete( '/account/deactivate'           )(self.deactivate_profile)

    async def get_user_profile(
            self, service: UserService = Depends(UserService)
            ) -> UserProfile:
        return await service.get_current_profile()

    async def update_profile(
            self, data: UpdateProfileRequest, service: UserService = Depends(UserService)
            ) -> UpdateProfileResponse:
        updated_user = await service.update_user_profile(data)
        return {
            "message": "Profile updated",
            "user": UserProfile.model_validate(updated_user)
        }

    async def update_account_type(
            self, data: UpgradeAccountRequest, service: UserService = Depends(UserService)
            ) -> MessageResponse:
        await service.update_account_type(data)
        return {"message": f"Account type changed to {data.account_type}"}

    async def update_password(
            self, data: UpdatePasswordRequest, service: UserService = Depends(UserService)
            ) -> MessageResponse:
        await service.update_user_password(data.old_password, data.new_password)
        return {"message": "Password updated successfully"}

    async def activate_profile(
            self, service: UserService = Depends(UserService)
            ) -> MessageResponse:
        await service.activate_current_user()
        return {"message": "Account activated"}

    async def deactivate_profile(
            self, service: UserService = Depends(UserService)
            ) -> MessageResponse:
        await service.deactivate_current_user()
        return {"message": "Account deactivated"}

class SuperAdminRoutes:
    def __init__(self, prefix: str = '/admin'):
        self.router = APIRouter(
                prefix=prefix, tags=["SuperAdmin"],
                dependencies=[authorization_level_required(AccountLevel.MODERATOR)]
            )

        self.router.get(    '/users'                        )(self.list_users)
        self.router.get(    '/user/{username}'              )(self.get_profile)
        self.router.delete( '/deactivate/{user_id}'         )(self.deactivate_user)
        self.router.delete( '/delete/{user_id}'             )(self.delete_user)

    async def list_users(
            self, page:int = 1, service: UserService = Depends(UserService)
            ) -> List[UserProfile]:
        users = await service.list_users(page)
        return [UserProfile.model_validate(user) for user in users]

    async def get_profile(
            self, username:str, service: UserService = Depends(UserService)
            ) -> UserProfile:
        user = await service.get_profile(username)
        return UserProfile.model_validate(user)

    async def deactivate_user(self, user_id:str, service: UserService = Depends(UserService)):
        await service.deactivate_user_by_user_id(user_id)
        return {"message": "User deactivated"}

    async def delete_user(self, user_id: str, service: UserService = Depends(UserService)):
        await service.delete_user_by_user_id(user_id)
        return {"message": "User deleted"}
