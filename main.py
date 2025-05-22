import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy.engine.url import make_url
import uvicorn

from common.database import engine
from common.logger import logger
from common.middleware import AccessLogMiddleware
from config import settings
from api.router import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This will initialize the local sqlite db
    # for docker and testing sessions

    db_url = make_url(settings.DATABASE_URL)
    if db_url.drivername.startswith('sqlite') and \
            not os.path.exists(db_url.database):
        from common.database import setup_dev_env
        setup_dev_env()
        logger.warn("There was no DATABASE_URL provided\nfalling back to sqlite3")

    yield
    await engine.dispose()

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)
app.include_router(
        router,
        prefix='/api/' + settings.API_VERSION
    )

app.add_middleware(AccessLogMiddleware)

@app.get("/")
async def health_check():
    logger.debug("checking if this is working")
    return {"status": "ok"}

#TODO: Remove this after development
@app.get("/settings")
async def get_settings():
    return settings.__dict__

if __name__ == "__main__":
    uvicorn.run(
        'main:app',
        host="0.0.0.0",
        port=8000,
        reload=not(settings.is_production_server())
    )
