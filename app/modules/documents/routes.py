from fastapi import APIRouter, Form, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.common.database import get_db
from app.common.dependencies import authorization_level_required, get_current_user
from app.modules.users.models import User, AccountLevel
from app.modules.documents import service
from app.modules.documents.schemas import DocumentResponse

router = APIRouter()

@router.put("/upload", response_model=DocumentResponse)
async def upload_document(
    title: str = Form(...),
    is_private: bool = Form(False),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(authorization_level_required(AccountLevel.BASIC))
):

    return await service.upload_document(
        db=db,
        user=current_user,
        file=file,
        title=title,
        is_private=is_private
    )


@router.patch("/upload", response_model=DocumentResponse)
async def reupload_document(
    document_key:str = Form(...),
    title: Optional[str] = Form(...),
    is_private: Optional[bool] = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(authorization_level_required(AccountLevel.PREMIUM))
):
    return await service.upload_document(
        db=db,
        user=current_user,
        document_key=document_key,
        file=file,
        title=title,
        is_private=is_private,
        is_reupload=True
    )


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await service.delete_document(db, document_id, current_user)
    return


@router.get("/public", response_model=List[DocumentResponse])
async def list_public_documents(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    return await service.list_public_documents(db=db, skip=skip, limit=limit)


@router.get("/user/{username}", response_model=List[DocumentResponse])
async def get_public_documents_by_user(
    username: str,
    db: AsyncSession = Depends(get_db)
):
    return await service.get_public_documents_by_user(db, username)


@router.get("/me", response_model=List[DocumentResponse])
async def list_my_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.list_user_documents(db, current_user.id)
