from pydantic import BaseModel
from datetime import datetime

# Request schemas
class RegisterRequest(BaseModel):
    username: str = 'ctadel'
    email:str = 'nep.prajwal@gmail.com'
    password: str = 'somethingwild'
    full_name:str = 'Prajwal Dev'

class LoginRequest(BaseModel):
    username: str = 'ctadel'
    password: str = 'somethingwild'

class UpdateProfileRequest(BaseModel):
    full_name:str = 'Prajwal Dev'
    email:str = 'nep.prajwal@gmail.com'

class UpdatePasswordRequest(BaseModel):
    old_password: str = 'somethingwild'
    new_password: str = 'evenmorewild'

class UpgradeAccountRequest(BaseModel):
    account_type: str = 'PREMIUM'

# Responses
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserProfile(BaseModel):
    id:int = 1
    username:str = 'ctadel'
    full_name:str = 'Prajwal Dev'
    email:str = 'nep.prajwal@gmail.com'
    account_type:str = 'PREMIUM'
    created_at:datetime = '2025-11-25 10:42:12'

    model_config = {
        "from_attributes": True
    }

class MessageResponse(BaseModel):
    message:str = "Something just like this"

class UpdateProfileResponse(MessageResponse):
    user:UserProfile
