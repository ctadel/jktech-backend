from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from common.database import get_db
from common.auth import decode_access_token
from modules.users import crud as user_crud
from config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/{settings.API_VERSION}/users/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = user_crud.get_user_by_id(db, user_id=payload.get("sub"))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user

def require_role(role: str):
    def role_checker(current_user=Depends(get_current_user)):
        if current_user.role != role:
            raise HTTPException(status_code=403, detail="Access denied")
        return current_user
    return role_checker
