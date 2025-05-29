import os
import pytest_asyncio
import asyncio
from httpx import AsyncClient
from sqlalchemy import make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.common.database import get_db, Base  # Ensure Base is imported here
from app.common.auth import hash_password
from app.modules.users.models import User, AccountLevel
from app.config import settings

# Use SQLite test DB
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Set up engine and sessionmaker globally
engine_test = create_async_engine(TEST_DATABASE_URL, future=True, echo=False)
TestingSessionLocal = sessionmaker(bind=engine_test, class_=AsyncSession, expire_on_commit=False)

@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# Create test DB schema once before tests
@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_test_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine_test.dispose()
    db_url = make_url(TEST_DATABASE_URL)
    if os.path.exists(db_url.database):
        os.remove(db_url.database)

# Provide a clean session per test
@pytest_asyncio.fixture
async def db():
    async with TestingSessionLocal() as session:
        yield session

# Override FastAPI's get_db dependency
@pytest_asyncio.fixture
async def client(db: AsyncSession):
    async def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url=f"http://localhost") as ac:
        yield ac

# Create a test user
@pytest_asyncio.fixture
async def test_user(db: AsyncSession):
    user = User(
        username="ctadel",
        full_name="Prajwal Dev",
        email="prajwal@jktech.com",
        account_type=AccountLevel.BASIC.name,
        hashed_password=hash_password("testpass")
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
