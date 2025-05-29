import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.engine.url import make_url

from app.common.database import engine
from app.common.logger import logger
from app.common.middleware import AccessLogMiddleware
from app.config import settings
from app.api.router import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This will initialize the local sqlite db
    # for docker and testing sessions

    db_url = make_url(settings.DATABASE_URL)
    if db_url.drivername.startswith('sqlite') and \
            not os.path.exists(db_url.database):
        from app.common.database import initialize_tables
        initialize_tables()
        logger.warn("There was no DATABASE_URL provided\nfalling back to sqlite3")

    yield
    await engine.dispose()

app = FastAPI(
        title=settings.PROJECT_NAME,
        lifespan=lifespan,
        version=settings.API_VERSION
    )

app.include_router(router,
        prefix = '/api/' + settings.API_VERSION)

app.add_middleware(AccessLogMiddleware)
app.add_middleware(CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health_check():
    return {"status": "ok"}

#TODO: Remove this after development
@app.get("/settings")
async def get_settings():
    return settings.__dict__
