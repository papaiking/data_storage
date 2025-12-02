from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Integer, DateTime, LargeBinary
from app.config import settings
import datetime

DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

class Metadata(Base):
    __tablename__ = "metadata"

    id = Column(Integer, primary_key=True, index=True)
    object_id = Column(String(255), unique=True, index=True, nullable=False)
    size = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    storage_type = Column(String(50), nullable=False)
    file_path = Column(String(1024), nullable=True) # For local storage

class BlobData(Base):
    __tablename__ = "blob_data"
    id = Column(Integer, primary_key=True, index=True)
    object_id = Column(String(255), unique=True, index=True, nullable=False)
    data = Column(LargeBinary, nullable=False)


async def get_db():
    async with async_session() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)