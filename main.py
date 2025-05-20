from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn

from common.database import engine
from config import settings
from api.router import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)
app.include_router(
        router,
        prefix='/api/' + settings.API_VERSION
    )

@app.get("/")
async def health_check():
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
