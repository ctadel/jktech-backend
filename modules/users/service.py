from sqlalchemy.orm import Session
from common.auth import hash_password, verify_password, create_access_token
from modules.users import crud
from modules.users.schemas import *
from common.exceptions import InvalidCredentialsException

async def register_user(db: Session, data:RegisterRequest):
    hashed_pw = hash_password(data.password)
    return await crud.create_user(db, data, hashed_pw)

async def authenticate_user(db: Session, username: str, password: str):
    user = await crud.get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        raise InvalidCredentialsException()
    return user

def generate_token(user):
    return create_access_token({"sub": str(user.id), "role": user.role})
