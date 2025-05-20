from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "JK Tech QnA"
    API_VERSION: str = "v1"
    ENV:str = 'PROD'
    LOG_DIRECTORY:str = 'logs'

    DATABASE_URL: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    CORS_ALLOWED_ORIGINS: str = "*"

    @property
    def CORS_ORIGINS(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"

    def is_production_server(self):
        return self.ENV.upper() == 'PROD'

settings = Settings()
