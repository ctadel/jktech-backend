from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import create_engine as sync_create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, future=True, echo=False)
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with async_session() as session:
        yield session

def setup_dev_env():
    # Couldn't find the async Base, therefore I had to convert this to create a db
    # It's a one time thing
    sync_url = settings.DATABASE_URL.replace("sqlite+aiosqlite", "sqlite")

    sync_engine = sync_create_engine(sync_url, future=True, echo=False)
    Base.metadata.create_all(bind=sync_engine)
