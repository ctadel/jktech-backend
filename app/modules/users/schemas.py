from pydantic import BaseModel
from datetime import datetime

# Request schemas
class RegisterRequest(BaseModel):
    username: str
    email:str
    password: str
    full_name:str

class LoginRequest(BaseModel):
    username: str
    password: str

class UpdateProfileRequest(BaseModel):
    full_name:str
    email:str

class UpdatePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class UpgradeAccountRequest(BaseModel):
    account_type: str

# Responses
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserProfile(BaseModel):
    id:int
    username:str
    full_name:str
    email:str
    account_type:str
    created_at:datetime

