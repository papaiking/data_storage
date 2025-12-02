from pydantic import BaseModel, validator, field_validator
import base64
from datetime import datetime

class BlobStoreRequest(BaseModel):
    id: str
    data: str

    @field_validator('data')
    def data_must_be_base64(cls, v):
        try:
            base64.b64decode(v)
        except (ValueError, TypeError):
            raise ValueError('Data must be a valid base64 string')
        return v

class BlobGetResponse(BaseModel):
    id: str
    data: str
    size: int
    created_at: datetime
