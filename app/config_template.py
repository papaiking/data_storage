import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """Initializes and returns a logger."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

# from pydantic import BaseSettings

# class Settings(BaseSettings):
class Settings():
    # Security
    SECRET_KEY: str = "76134SBNVDSDHGWF25462567523"
    ALGORITHM: str = "HS256"

    # Storage
    ACTIVE_STORAGE: str = "database"  # 'local', 'database', or 's3'

    # Local storage config
    LOCAL_STORAGE_PATH: str = "_blob_storage"

    # Configuration for S3 storage
    S3_ACCESS_KEY_ID: str = "xxxxxx"
    S3_SECRET_ACCESS_KEY: str = "xxxxxx"
    S3_BUCKET_NAME: str = "hams-xxxxx"
    S3_REGION_NAME = "ap-xxxx"

    # Database (PostgreSQL)
    DB_USER: str = "hams"
    DB_PASSWORD: str = "xxxxxx"
    DB_HOST: str = "xxxxxx"
    DB_PORT: int = 5432
    DB_NAME: str = "hams_xxxxx"

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        case_sensitive = True

settings = Settings()
