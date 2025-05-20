from pydantic import BaseModel
from modules.users.models import UserRole

# Request schemas
class RegisterRequest(BaseModel):
    username: str
    email:str
    password: str
    full_name:str
    role:UserRole

class LoginRequest(BaseModel):
    username: str
    password: str

class RoleUpdateRequest(BaseModel):
    user_id: int
    role: UserRole

# Responses
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
