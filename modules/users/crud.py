from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from modules.users.models import User, UserRole
from common.exceptions import UserAlreadyExistsException, UserNotFoundException


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def create_user(
    db: AsyncSession,
    username: str,
    hashed_password: str,
    role: UserRole = UserRole.VIEWER
) -> User:
    if await get_user_by_username(db, username):
        raise UserAlreadyExistsException()

    user = User(username=username, hashed_password=hashed_password, role=role)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_role(db: AsyncSession, user_id: int, role: UserRole) -> User:
    user = await get_user_by_id(db, user_id)
    if not user:
        raise UserNotFoundException()

    user.role = role
    await db.commit()
    await db.refresh(user)
    return user
