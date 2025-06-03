from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.common.database import get_db
from app.common.auth import decode_access_token
from app.common.exceptions import InvalidAuthToken
from app.modules.users.models import AccountLevel, User
from app.modules.users import crud as user_crud
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/{settings.API_VERSION}/users/auth/token")

async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
        ) -> User:
    payload = decode_access_token(token)
    user = await user_crud.get_user_by_username(db, username=payload.get("username"))
    if not user:
        raise InvalidAuthToken("The user with this token does not exist")

    return user

async def get_optional_user(
        token: Optional[str] = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
        ) -> Optional[User]:
    if token is None:
        return None
    try:
        payload = decode_access_token(token)
        username = payload.get("username")
        user = user_crud.get_user_by_username(db, username)
        return user
    except Exception:
        return None

def authorization_level_required(required_level: AccountLevel = AccountLevel.BASIC):
    def dependency(user=Depends(get_current_user)):
        if AccountLevel[user.account_type] < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return user
    return Depends(dependency)
