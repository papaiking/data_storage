from fastapi import FastAPI
from routers import blob
from app.database import init_db
from app.config import settings
import os

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await init_db()
    if settings.ACTIVE_STORAGE == 'local':
        os.makedirs(settings.LOCAL_STORAGE_PATH, exist_ok=True)


app.include_router(blob.router)

@app.get("/")
async def root():
    return {"message": "ThucVX: Data Storage Service is running"}

