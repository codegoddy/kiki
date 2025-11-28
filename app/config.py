from pydantic import BaseSettings

class Settings(BaseSettings):
    database_hostname: str = "localhost"
    database_port: str = "5432"
    database_password: str = "password"
    database_name: str = "fastapi_db"
    database_username: str = "postgres"

    class Config:
        env_file = ".env"

settings = Settings()