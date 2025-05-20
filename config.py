from os import getenv
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "JK Tech QnA"
    API_VERSION: str = "v1"
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ENV:str = 'PROD'

    class Config:
        try:
            if env_name:=getenv('ENV','').lower():
                env_file = f'.env.{env_name}'
            else:
                env_file = ".env"
        except Exception as e:
            print("Exception while reading the environment (Using .env)\n", e)
            env_file = ".env"


    def is_production_server(self):
        return self.ENV.upper() == 'PROD'

settings = Settings()
