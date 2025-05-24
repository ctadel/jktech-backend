from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from functools import partial

from app.common.database import get_db
from app.common.auth import decode_access_token
from app.modules.users.models import AccountLevel
from app.modules.users import crud as user_crud
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/{settings.API_VERSION}/users/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = await user_crud.get_user_by_username(db, username=payload.get("username"))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invliad User Token")

    return user

def authorization_level_required(required_level: AccountLevel = AccountLevel.BASIC):
    def dependency(user=Depends(get_current_user)):
        if AccountLevel[user.account_type] < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return user
    return Depends(dependency)
