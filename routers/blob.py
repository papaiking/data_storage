from fastapi import APIRouter, Depends, HTTPException
from app.models import BlobStoreRequest, BlobGetResponse
from app.storage import get_storage_backend, BaseStorage
from app.auth import verify_token
from app.config import get_logger
import base64

router = APIRouter()
logger = get_logger(__name__)

@router.post("/v1/blobs", status_code=201, dependencies=[Depends(verify_token)])
async def store_blob(
    request: BlobStoreRequest,
    storage: BaseStorage = Depends(get_storage_backend)
):
    try:
        data = base64.b64decode(request.data)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid base64 data")
    except Exception as e:
        logger.error(f"Failed to decode base64 data: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Failed to decode base64 data: {e}")

    try:
        await storage.store(request.id, data)
    except Exception as e:
        logger.error(f"Failed to store blob: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to store blob: {e}")

    return {"message": "Blob stored successfully"}

@router.get("/v1/blobs/{blob_id}", response_model=BlobGetResponse, dependencies=[Depends(verify_token)])
async def retrieve_blob(
    blob_id: str,
    storage: BaseStorage = Depends(get_storage_backend)
):
    try:
        data, meta = await storage.retrieve(blob_id)
        response_data = base64.b64encode(data).decode('utf-8')

        return BlobGetResponse(
            id=meta.object_id,
            data=response_data,
            size=meta.size,
            created_at=meta.created_at
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Blob not found")
    except Exception as e:
        logger.error(f"Failed to retrieve blob: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve blob: {e}")
