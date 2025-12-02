from fastapi.testclient import TestClient
from main import app
from app.config import settings, get_logger
import base64
import uuid
import os
import datetime
from app.storage import get_storage_backend, BaseStorage
from unittest.mock import MagicMock
import pytest
from httpx import AsyncClient

logger = get_logger(__name__)

@pytest.mark.asyncio
async def test_http_store_and_retrieve_binary_blob():
    async with AsyncClient(base_url="http://127.0.0.1:8000") as client:
        # 1. Prepare data
        blob_id = str(uuid.uuid4())
        # Generate 1MB of random binary data
        original_data = os.urandom(1024 * 716)
        b64_data = base64.b64encode(original_data).decode('utf-8')

        headers = {
            "Authorization": f"Bearer {settings.SECRET_KEY}"
        }

        # 2. Store the blob
        store_response = await client.post(
            "/v1/blobs",
            headers=headers,
            json={"id": blob_id, "data": b64_data}
        )
        logger.info(f"Response: {store_response.json()}")
        assert store_response.status_code == 201
        assert store_response.json() == {"message": "Blob stored successfully"}

        # 3. Retrieve the blob
        retrieve_response = await client.get(
            f"/v1/blobs/{blob_id}",
            headers=headers
        )
        logger.info(f"Blob id: {blob_id}")
        
        assert retrieve_response.status_code == 200
        
        response_json = retrieve_response.json()
        retrieved_b64_data = response_json["data"]
        retrieved_data = base64.b64decode(retrieved_b64_data)

        assert response_json["id"] == blob_id
        assert retrieved_data == original_data
        assert response_json["size"] == len(original_data)

@pytest.mark.asyncio
async def test_retrieve_nonexistent_blob():
    blob_id = str(uuid.uuid4())
    headers = {
        "Authorization": f"Bearer {settings.SECRET_KEY}"
    }
    async with AsyncClient(base_url="http://127.0.0.1:8000") as client:
        response = await client.get(
            f"/v1/blobs/{blob_id}",
            headers=headers
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "Blob not found"}

@pytest.mark.asyncio
async def test_store_blob_invalid_token():
    blob_id = str(uuid.uuid4())
    original_data = b"test"
    b64_data = base64.b64encode(original_data).decode('utf-8')

    headers = {
        "Authorization": "Bearer invalidtoken"
    }
    async with AsyncClient(base_url="http://127.0.0.1:8000") as client:
        response = await client.post(
            "/v1/blobs",
            headers=headers,
            json={"id": blob_id, "data": b64_data}
        )
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_store_blob_invalid_base64():
    blob_id = str(uuid.uuid4())
    headers = {
        "Authorization": f"Bearer {settings.SECRET_KEY}"
    }
    async with AsyncClient(base_url="http://127.0.0.1:8000") as client:
        response = await client.post(
            "/v1/blobs",
            headers=headers,
            json={"id": blob_id, "data": "this is not base64"}
        )
        assert response.status_code == 422  # Check by validator
        logger.info(f"Ressponse: {response.json()}")
        # assert response.json() == {"detail": "Invalid base64 data"}