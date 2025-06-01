from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.modules.users.models import User, AccountLevel
from app.modules.users.schemas import RegisterRequest
from app.common.exceptions import AccountDeactivatedError, UserAlreadyExistsException, UserNotFoundException, InvalidUserParameters


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user:
        raise UserNotFoundException(username=username)
    if not user.is_active:
        raise AccountDeactivatedError()
    return user


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def create_user(
    db: AsyncSession,
    data:RegisterRequest,
    hashed_password: str,
) -> User:
    if await get_user_by_username(db, data.username):
        raise UserAlreadyExistsException(username=data.username)

    user_from_email = await db.execute(select(User).where(User.email == data.email))
    if user_from_email.first():
        raise UserAlreadyExistsException(email=data.email)

    data = data.model_dump(exclude=['password'])
    user = User(
            **data,
            hashed_password=hashed_password,
            account_type = AccountLevel.BASIC.name
        )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def update_user(
    db: AsyncSession,
    user:User,
    data:RegisterRequest,
) -> User:
    user_from_email = await db.execute(select(User).where(User.email == data.email))
    if user_from_email.first():
        raise InvalidUserParameters("Email already exists")

    if data.full_name is not None:
        user.full_name = data.full_name
    if data.email is not None:
        user.email = data.email

    await db.commit()
    await db.refresh(user)
    return user
